from __future__ import annotations

import os
from datetime import timedelta
from io import BytesIO
from pathlib import Path

from django.conf import settings


class LocalStorageService:
    """Disk-based storage used when USE_LOCAL_STORAGE=1 (no MinIO required)."""

    def __init__(self) -> None:
        self.media_root = Path(getattr(settings, "MEDIA_ROOT", settings.BASE_DIR / "media"))

    def _path(self, object_name: str) -> Path:
        return self.media_root / object_name

    def upload_bytes(self, object_name: str, content: bytes, content_type: str = "application/octet-stream") -> str:
        dest = self._path(object_name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
        return object_name

    def stat(self, object_name: str):
        p = self._path(object_name)
        if not p.exists():
            raise FileNotFoundError(f"Object not found: {object_name}")
        return {"size": p.stat().st_size, "path": str(p)}

    def download_bytes(self, object_name: str) -> bytes:
        return self._path(object_name).read_bytes()

    def presigned_get_url(self, object_name: str, expires_minutes: int = 60) -> str:
        # Return a local media URL — served by Django in DEBUG mode
        return f"{getattr(settings, 'MEDIA_URL', '/media/')}{object_name}"

    def presigned_put_url(self, object_name: str, expires_minutes: int = 30) -> str:
        # No pre-signed PUT for local storage; return empty string
        return ""

    def delete(self, object_name: str) -> None:
        p = self._path(object_name)
        if p.exists():
            p.unlink()


class MinioStorageService:
    """MinIO/S3 storage used when USE_LOCAL_STORAGE=0."""

    def __init__(self) -> None:
        from minio import Minio
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket = settings.MINIO_BUCKET

    def ensure_bucket(self) -> None:
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def upload_bytes(self, object_name: str, content: bytes, content_type: str = "application/octet-stream") -> str:
        self.ensure_bucket()
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_name,
            data=BytesIO(content),
            length=len(content),
            content_type=content_type,
        )
        return object_name

    def stat(self, object_name: str):
        self.ensure_bucket()
        return self.client.stat_object(self.bucket, object_name)

    def download_bytes(self, object_name: str) -> bytes:
        self.ensure_bucket()
        response = self.client.get_object(self.bucket, object_name)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def presigned_get_url(self, object_name: str, expires_minutes: int = 60) -> str:
        self.ensure_bucket()
        return self.client.presigned_get_object(
            self.bucket, object_name, expires=timedelta(minutes=expires_minutes)
        )

    def presigned_put_url(self, object_name: str, expires_minutes: int = 30) -> str:
        self.ensure_bucket()
        return self.client.presigned_put_object(
            self.bucket, object_name, expires=timedelta(minutes=expires_minutes)
        )

    def delete(self, object_name: str) -> None:
        try:
            self.client.remove_object(self.bucket, object_name)
        except Exception:
            pass


def _build_storage():
    if getattr(settings, "USE_LOCAL_STORAGE", True):
        return LocalStorageService()
    return MinioStorageService()


minio_storage = _build_storage()
