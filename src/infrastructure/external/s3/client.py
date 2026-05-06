from contextlib import AsyncExitStack
from io import BytesIO
from typing import BinaryIO, Union

import aiobotocore.session
from aiobotocore.config import AioConfig
from botocore.exceptions import ClientError

from src.settings import settings


# ============================================================
# Сам клиент
# ============================================================
class S3Client:
    def __init__(self):
        self.settings = settings
        self._client = None
        self._exit_stack = None

    async def start(self) -> None:
        """Инициализация клиента – вызвать один раз при старте приложения."""
        self._exit_stack = AsyncExitStack()
        session = aiobotocore.session.get_session()
        config = AioConfig(
            max_pool_connections=self.settings.s3.max_pool_connections,
            connect_timeout=self.settings.s3.connect_timeout,
            read_timeout=self.settings.s3.read_timeout,
            retries={
                "mode": self.settings.s3.retry_mode,
                "max_attempts": self.settings.s3.max_retries,
            },
        )
        self._client = await self._exit_stack.enter_async_context(
            session.create_client(
                "s3",
                endpoint_url=self.settings.s3.endpoint_url,
                aws_access_key_id=self.settings.s3.access_key,
                aws_secret_access_key=self.settings.s3.secret_key,
                region_name=self.settings.s3.region,
                config=config,
            )
        )

    async def stop(self) -> None:
        """Корректное закрытие – вызвать при выключении приложения."""
        if self._exit_stack:
            await self._exit_stack.aclose()
        self._client = None

    async def upload_file(
        self,
        key: str,
        data: Union[bytes, BinaryIO],
        content_type: str = "application/octet-stream",
        bucket: str = None,
    ) -> None:
        """
        Загружает файл в S3.
        - data: могут быть как bytes, так и файлоподобный объект (BinaryIO).
        - bucket: если не передан, используется bucket из настроек.
        """
        bucket = bucket or self.settings.s3.bucket

        # Поддерживаем bytes -> оборачиваем в BytesIO для унификации
        if isinstance(data, bytes):
            data = BytesIO(data)

        try:
            await self._client.put_object(
                Bucket=bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
            )
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code")
            if error_code == "AccessDenied":
                raise PermissionError(f"Access denied to S3 bucket '{bucket}'")
            raise RuntimeError(f"S3 upload failed: {error_code}") from exc

    async def download_bytes(self, key: str, bucket: str = None) -> bytes:
        """Скачивает файл целиком в память (только для маленьких файлов)."""
        bucket = bucket or self.settings.bucket
        try:
            resp = await self._client.get_object(Bucket=bucket, Key=key)
            async with resp["Body"] as stream:
                return await stream.read()
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") == "NoSuchKey":
                return None
            raise

    async def get_presigned_url(
        self,
        key: str,
        method: str = "get_object",
        expires_in: int = 3600,
        bucket: str = None,
    ) -> str:
        """
        Генерирует presigned URL для временного доступа (например, для фронтенда).
        По умолчанию – на чтение (GET).
        """
        bucket = bucket or self.settings.bucket
        client_method = "get_object" if method == "GET" else "put_object"
        try:
            url = await self._client.generate_presigned_url(
                ClientMethod=client_method,
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expires_in,
                HttpMethod=method,
            )
            return url
        except ClientError as exc:
            raise RuntimeError(f"Failed to generate presigned URL: {exc}") from exc

    async def delete_file(self, key: str, bucket: str = None) -> None:
        bucket = bucket or self.settings.bucket
        try:
            await self._client.delete_object(Bucket=bucket, Key=key)
        except ClientError as exc:
            raise RuntimeError(f"Failed to delete {key}: {exc}") from exc


s3_client = S3Client()
