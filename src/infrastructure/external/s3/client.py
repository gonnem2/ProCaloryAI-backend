from contextlib import AsyncExitStack
from io import BytesIO

import aiobotocore.session
from aiobotocore.config import AioConfig
from botocore.exceptions import ClientError

from src.settings import settings


class S3Client:
    def __init__(self):
        self._internal = None  # minio:9000 — для backend операций
        self._public = None  # 10.0.2.2/storage — для URL которые уходят наружу

    async def start(self) -> None:
        session = aiobotocore.session.get_session()
        config = AioConfig(
            max_pool_connections=settings.s3.max_pool_connections,
            connect_timeout=settings.s3.connect_timeout,
            read_timeout=settings.s3.read_timeout,
            retries={
                "mode": settings.s3.retry_mode,
                "max_attempts": settings.s3.max_retries,
            },
        )
        self._exit_stack = AsyncExitStack()

        # Клиент 1 — внутренний, бэкенд → MinIO напрямую
        self._internal = await self._exit_stack.enter_async_context(
            session.create_client(
                "s3",
                endpoint_url=settings.s3.endpoint_url,  # http://minio:9000
                aws_access_key_id=settings.s3.access_key,
                aws_secret_access_key=settings.s3.secret_key,
                region_name=settings.s3.region,
                config=config,
            )
        )

        # Клиент 2 — публичный, генерирует URL для внешних клиентов
        self._public = await self._exit_stack.enter_async_context(
            session.create_client(
                "s3",
                endpoint_url=settings.s3.public_url,  # http://10.0.2.2/storage
                aws_access_key_id=settings.s3.access_key,
                aws_secret_access_key=settings.s3.secret_key,
                region_name=settings.s3.region,
            )
        )

    async def stop(self) -> None:
        if self._exit_stack:
            await self._exit_stack.aclose()
        self._internal = None
        self._public = None

    # ── Внутренние операции (backend → MinIO) ──────────────────

    async def upload_file(
        self, key: str, data, content_type="application/octet-stream", bucket=None
    ) -> None:
        """Backend сам загружает файл в MinIO"""
        bucket = bucket or settings.s3.bucket
        if isinstance(data, bytes):
            data = BytesIO(data)
        await self._internal.put_object(
            Bucket=bucket, Key=key, Body=data, ContentType=content_type
        )

    async def download_bytes(self, key: str, bucket=None) -> bytes | None:
        """Backend скачивает файл из MinIO"""
        bucket = bucket or settings.s3.bucket
        try:
            resp = await self._internal.get_object(Bucket=bucket, Key=key)
            async with resp["Body"] as stream:
                return await stream.read()
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "NoSuchKey":
                return None
            raise

    async def delete_file(self, key: str, bucket=None) -> None:
        bucket = bucket or settings.s3.bucket
        await self._internal.delete_object(Bucket=bucket, Key=key)

    # ── Публичные URL (для Android и AI Core) ──────────────────

    async def get_presigned_upload_url(
        self,
        key: str,
        expires_in: int = 300,
        bucket=None,
        content_type: str = "image/jpeg",  # ← добавить
    ) -> str:
        """
        Presigned PUT URL для Android.
        Android загружает фото напрямую в MinIO через nginx.
        """
        bucket = bucket or settings.s3.bucket
        return await self._public.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": bucket,
                "Key": key,
                "ContentType": content_type,  # ← подпись включает Content-Type
            },
            ExpiresIn=expires_in,
            HttpMethod="PUT",
        )

    async def get_internal_presigned_url(
            self, key: str, expires_in: int = 3600, bucket=None,
    ) -> str:
        """
        Presigned GET URL для AI Core.
        Подписан для minio:9000 — AI Core достучится напрямую внутри Docker.
        """
        bucket = bucket or settings.s3.bucket
        return await self._internal.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
            HttpMethod="GET",
        )

    def get_public_url(self, s3_key: str) -> str:
        """
        Публичная ссылка на файл для AI Core (Colab).
        AI Core скачивает фото по этому URL для анализа.
        """
        return f"{settings.s3.public_url}/{settings.s3.bucket}/{s3_key}"


s3_client = S3Client()
