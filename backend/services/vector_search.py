from __future__ import annotations

import math
from typing import Any

from django.conf import settings

from .mongodb import mongo_service

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover
    SentenceTransformer = None


class VectorSearchService:
    def __init__(self) -> None:
        self._model = None
        self._model_failed = False
        self.embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.target_dimensions = int(getattr(settings, "EMBEDDING_VECTOR_DIMENSIONS", 165))

    def _load_model(self):
        if self._model is not None:
            return self._model
        if self._model_failed or SentenceTransformer is None:
            return None
        try:
            self._model = SentenceTransformer(self.embedding_model_name)
            return self._model
        except Exception:
            self._model_failed = True
            return None

    def _normalize_dimensions(self, vector: list[float]) -> list[float]:
        if len(vector) >= self.target_dimensions:
            return vector[: self.target_dimensions]
        return vector + [0.0] * (self.target_dimensions - len(vector))

    def embed_text(self, text: str) -> list[float] | None:
        clean_text = (text or "").strip()
        if not clean_text:
            return None

        model = self._load_model()
        if model is None:
            return None

        vector = model.encode(clean_text, normalize_embeddings=True)
        float_vector = [float(item) for item in vector]
        return self._normalize_dimensions(float_vector)

    def ensure_indexes(self) -> dict[str, Any]:
        mongo_service.collection("documents").create_index("document_id", unique=True)
        mongo_service.collection("documents").create_index("status")
        mongo_service.collection("documents").create_index([("title", "text"), ("raw_text", "text"), ("searchable_summary", "text")])
        mongo_service.collection("documents").create_index("checksum")
        mongo_service.collection("reviews").create_index("next_action")
        mongo_service.collection("audit_logs").create_index("document_id")
        mongo_service.collection("pages").create_index([("document_id", 1), ("page_number", 1)], unique=True)

        vector_index_ready = False
        if getattr(settings, "MONGODB_ENABLE_VECTOR_SEARCH", True):
            try:
                mongo_service.db.command(
                    {
                        "createSearchIndexes": "documents",
                        "indexes": [
                            {
                                "name": settings.MONGODB_VECTOR_INDEX,
                                "type": "vectorSearch",
                                "definition": {
                                    "fields": [
                                        {
                                            "type": "vector",
                                            "path": "vector_embedding",
                                            "numDimensions": self.target_dimensions,
                                            "similarity": "cosine",
                                        }
                                    ]
                                },
                            }
                        ],
                    }
                )
                vector_index_ready = True
            except Exception:
                vector_index_ready = False

        return {
            "vector_index_name": settings.MONGODB_VECTOR_INDEX,
            "vector_dimensions": self.target_dimensions,
            "vector_search_enabled": vector_index_ready,
            "strategy": "MongoDB Vector Search when available; local cosine ranking and Mongo text search fallback",
        }

    def update_document_embedding(self, document_id: str, text: str) -> bool:
        embedding = self.embed_text(text)
        if not embedding:
            return False

        mongo_service.update_one(
            "documents",
            {"document_id": document_id},
            {
                "vector_embedding": embedding,
                "embedding_model": self.embedding_model_name,
                "vector_dimensions": self.target_dimensions,
            },
        )
        return True

    @staticmethod
    def _dot(a: list[float], b: list[float]) -> float:
        return sum(x * y for x, y in zip(a, b))

    @staticmethod
    def _magnitude(vec: list[float]) -> float:
        return math.sqrt(sum(value * value for value in vec))

    def _semantic_rank_atlas(self, query_embedding: list[float], limit: int, base_filter: dict[str, Any]) -> list[dict[str, Any]]:
        if not getattr(settings, "MONGODB_ENABLE_VECTOR_SEARCH", True):
            return []

        try:
            vector_stage: dict[str, Any] = {
                "$vectorSearch": {
                    "index": settings.MONGODB_VECTOR_INDEX,
                    "path": "vector_embedding",
                    "queryVector": query_embedding,
                    "numCandidates": max(limit * 20, 150),
                    "limit": limit,
                }
            }
            if base_filter:
                vector_stage["$vectorSearch"]["filter"] = base_filter

            pipeline = [
                vector_stage,
                {"$addFields": {"semantic_score": {"$meta": "vectorSearchScore"}}},
            ]
            return list(mongo_service.collection("documents").aggregate(pipeline))
        except Exception:
            return []

    def _semantic_rank_local(self, query_embedding: list[float], limit: int, base_filter: dict[str, Any]) -> list[dict[str, Any]]:
        candidate_limit = max(limit * 25, 250)
        candidates = mongo_service.find_many("documents", base_filter, limit=candidate_limit, sort=[("updated_at", -1)])

        scored = []
        query_norm = self._magnitude(query_embedding)
        if query_norm == 0:
            return []

        for item in candidates:
            vector = item.get("vector_embedding")
            if not isinstance(vector, list):
                continue
            norm_vector = self._normalize_dimensions([float(v) for v in vector])
            vector_norm = self._magnitude(norm_vector)
            if vector_norm == 0:
                continue
            score = self._dot(query_embedding, norm_vector) / (query_norm * vector_norm)
            scored.append({**item, "semantic_score": round(float(score), 6)})

        scored.sort(key=lambda row: row.get("semantic_score", 0.0), reverse=True)
        return scored[:limit]

    def semantic_search(self, query: str, limit: int = 10, base_filter: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        base_filter = base_filter or {}
        clean_query = (query or "").strip()

        if not clean_query:
            return mongo_service.find_many("documents", base_filter, limit=limit, sort=[("updated_at", -1)])

        query_embedding = self.embed_text(clean_query)
        if query_embedding:
            atlas_results = self._semantic_rank_atlas(query_embedding, limit=limit, base_filter=base_filter)
            if atlas_results:
                return atlas_results

            local_results = self._semantic_rank_local(query_embedding, limit=limit, base_filter=base_filter)
            if local_results:
                return local_results

        mongo_query = {"$and": [base_filter, {"$text": {"$search": clean_query}}]} if base_filter else {"$text": {"$search": clean_query}}
        return mongo_service.find_many("documents", mongo_query, limit=limit, sort=[("updated_at", -1)])


vector_search_service = VectorSearchService()
