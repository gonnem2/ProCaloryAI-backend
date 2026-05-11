from botocore.exceptions import ClientError

from src.api.graphql.schema import logger
from src.infrastructure.external.s3.client import s3_client
from src.settings import settings


async def ensure_bucket_exists(bucket: str = None) -> None:
    bucket = bucket or settings.s3.bucket
    try:
        await s3_client._internal.head_bucket(Bucket=bucket)
    except ClientError as exc:
        if exc.response["Error"]["Code"] in ("404", "NoSuchBucket"):
            await s3_client._internal.create_bucket(Bucket=bucket)
            logger.info("Created S3 bucket: %s", bucket)
        else:
            raise
