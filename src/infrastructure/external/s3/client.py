import uuid
import aiobotocore.session
from src.settings import settings


class S3Client:
    def __init__(self):
        self._session = aiobotocore.session.get_session()

    async def upload_photo(
        self, photo_bytes: bytes, content_type: str = "image/jpeg"
    ) -> str:
        """Загружает фото, возвращает s3_key"""
        key = f"photos/{uuid.uuid4()}.jpg"

        async with self._session.create_client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
        ) as client:
            await client.put_object(
                Bucket=settings.S3_BUCKET,
                Key=key,
                Body=photo_bytes,
                ContentType=content_type,
            )

        return key

    def get_url(self, s3_key: str) -> str:
        return f"{settings.S3_ENDPOINT_URL}/{settings.S3_BUCKET}/{s3_key}"


s3_client = S3Client()
