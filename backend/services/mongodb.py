from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from django.conf import settings
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection

logger = logging.getLogger(__name__)


class MongoService:
    _instance: MongoService | None = None

    def __init__(self) -> None:
        self.client = MongoClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=10000,
        )
        self.db = self.client[settings.MONGODB_DB_NAME]

    def collection(self, name: str) -> Collection:
        return self.db[name]

    def insert_one(self, name: str, document: dict[str, Any]) -> Any:
        now = self.utcnow()
        payload = {**document, "updated_at": now}
        payload.setdefault("created_at", now)
        return self.collection(name).insert_one(payload)

    def find_one(self, name: str, query: dict[str, Any]) -> dict[str, Any] | None:
        return self.collection(name).find_one(query, {"_id": 0})

    def find_many(
        self,
        name: str,
        query: dict[str, Any],
        limit: int = 50,
        sort: list[tuple[str, int]] | None = None,
        projection: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        proj = projection or {"_id": 0}
        cursor = self.collection(name).find(query, proj)
        if sort:
            cursor = cursor.sort(sort)
        return list(cursor.limit(limit))

    def update_one(self, name: str, query: dict[str, Any], update: dict[str, Any]) -> None:
        self.collection(name).update_one(
            query,
            {"$set": {**update, "updated_at": self.utcnow()}},
            upsert=False,
        )

    def upsert_one(self, name: str, query: dict[str, Any], update: dict[str, Any]) -> None:
        now = self.utcnow()
        self.collection(name).update_one(
            query,
            {
                "$set": {**update, "updated_at": now},
                "$setOnInsert": {"created_at": update.get("created_at", now)},
            },
            upsert=True,
        )

    def delete_one(self, name: str, query: dict[str, Any]) -> None:
        self.collection(name).delete_one(query)

    def delete_many(self, name: str, query: dict[str, Any]) -> None:
        self.collection(name).delete_many(query)

    def count(self, name: str, query: dict[str, Any]) -> int:
        return self.collection(name).count_documents(query)

    def append_audit_log(self, document_id: str, event_type: str, payload: dict[str, Any]) -> None:
        self.insert_one(
            "audit_logs",
            {
                "document_id": document_id,
                "event_type": event_type,
                "payload": payload,
                "occurred_at": self.utcnow(),
            },
        )

    @staticmethod
    def utcnow() -> datetime:
        return datetime.now(timezone.utc)


mongo_service = MongoService()
