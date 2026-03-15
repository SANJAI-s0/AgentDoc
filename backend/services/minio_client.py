from __future__ import annotations

from datetime import timedelta
from io import BytesIO

from django.conf import settings
from minio import Minio


class MinioStorageService:
    def __init__(self) -> None:
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
        stream = BytesIO(content)
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_name,
            data=stream,
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
            self.bucket,
            object_name,
            expires=timedelta(minutes=expires_minutes),
        )

    def presigned_put_url(self, object_name: str, expires_minutes: int = 30) -> str:
        self.ensure_bucket()
        return self.client.presigned_put_object(
            self.bucket,
            object_name,
            expires=timedelta(minutes=expires_minutes),
        )


minio_storage = MinioStorageService()
