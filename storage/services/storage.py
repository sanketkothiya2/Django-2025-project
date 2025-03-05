from minio import Minio
from django.conf import settings
import hashlib
import os

class MinioStorage:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        if not self.client.bucket_exists(settings.MINIO_BUCKET_NAME):
            self.client.make_bucket(settings.MINIO_BUCKET_NAME)

    def upload_chunk(self, file_id, chunk_number, data):
        object_name = f"{file_id}/{chunk_number}"
        self.client.put_object(
            settings.MINIO_BUCKET_NAME,
            object_name,
            data,
            len(data)
        )
        return object_name

    def download_chunk(self, object_name):
        try:
            data = self.client.get_object(
                settings.MINIO_BUCKET_NAME,
                object_name
            )
            return data.read()
        except Exception as e:
            print(f"Error downloading chunk: {e}")
            return None