from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from django.conf import settings
from pymongo import MongoClient
from pymongo.collection import Collection


class MongoService:
    def __init__(self) -> None:
        self.client = MongoClient(settings.MONGODB_URI)
        self.db = self.client[settings.MONGODB_DB_NAME]

    def collection(self, name: str) -> Collection:
        return self.db[name]

    def insert_one(self, name: str, document: dict[str, Any]) -> Any:
        payload = {**document, "updated_at": self.utcnow()}
        if "created_at" not in payload:
            payload["created_at"] = self.utcnow()
        return self.collection(name).insert_one(payload)

    def find_one(self, name: str, query: dict[str, Any]) -> dict[str, Any] | None:
        return self.collection(name).find_one(query)

    def find_many(self, name: str, query: dict[str, Any], limit: int = 50, sort: list[tuple[str, int]] | None = None):
        cursor = self.collection(name).find(query)
        if sort:
            cursor = cursor.sort(sort)
        return list(cursor.limit(limit))

    def update_one(self, name: str, query: dict[str, Any], update: dict[str, Any]) -> None:
        self.collection(name).update_one(query, {"$set": {**update, "updated_at": self.utcnow()}}, upsert=False)

    def upsert_one(self, name: str, query: dict[str, Any], update: dict[str, Any]) -> None:
        created_at = update.get("created_at", self.utcnow())
        self.collection(name).update_one(
            query,
            {
                "$set": {**update, "updated_at": self.utcnow()},
                "$setOnInsert": {"created_at": created_at},
            },
            upsert=True,
        )

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
