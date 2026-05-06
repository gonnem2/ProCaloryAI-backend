import uuid
import logging

from src.domain.models import AnalysisRequest
from src.domain.models.meal_log import MealLog, MealType, MealSource

from src.infrastructure.external.kafka.producer import kafka_producer
from src.infrastructure.external.s3.client import s3_client
from src.infrastructure.uow import AbstractUnitOfWork

logger = logging.getLogger(__name__)


class AnalysisService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def request_upload_url(self, user_id: int) -> dict:
        """
        Шаг 1: создаём AnalysisRequest, генерируем presigned PUT URL.
        Фронт загружает фото напрямую в S3 по этому URL.
        """
        s3_key = f"photos/{user_id}/{uuid.uuid4()}.jpg"
        presigned_url = await s3_client.get_presigned_url(
            key=s3_key,
            method="PUT",
            expires_in=300,  # 5 минут на загрузку
        )

        request = AnalysisRequest.create(user_id=user_id, s3_key=s3_key)
        await self.uow.analysis_repo.add(request)
        await self.uow.commit()

        return {
            "request_id": request.id,
            "upload_url": presigned_url,
            "s3_key": s3_key,
            "expires_in": 300,
        }

    async def confirm_upload_and_analyze(self, user_id: int, request_id: int) -> dict:
        """
        Шаг 2: фронт подтверждает загрузку → отправляем задачу в Kafka.
        """
        request = await self.uow.analysis_repo.get(request_id)
        if not request or request.user_id != user_id:
            raise ValueError("Analysis request not found")

        request.mark_uploaded()
        request.mark_processing()
        await self.uow.commit()

        s3_url = s3_client.get_url(request.s3_key)
        await kafka_producer.send(
            "photo.analysis.requested",
            {
                "request_id": request.id,
                "user_id": user_id,
                "s3_url": s3_url,
            },
        )

        logger.info("Analysis requested: request_id=%s user_id=%s", request.id, user_id)
        return {"request_id": request.id, "status": "processing"}

    async def handle_analysis_result(self, data: dict) -> None:
        """
        Колбэк Kafka consumer — приходит результат от AI Core.
        data: {request_id, dish_name, calories, protein, fat, carbs}
        """
        request = await self.uow.analysis_repo.get(data["request_id"])
        if not request:
            logger.warning("Unknown request_id: %s", data["request_id"])
            return

        log = MealLog.create(
            user_id=request.user_id,
            name=data["dish_name"],
            calories=data["calories"],
            protein=data["protein"],
            fat=data["fat"],
            carbs=data["carbs"],
            meal_type=MealType.snack,
            source=MealSource.camera,
            s3_key=request.s3_key,
        )
        await self.uow.meal_log_repo.add(log)
        await self.uow.commit()

        request.complete(meal_log_id=log.id, result=data)
        await self.uow.commit()

        logger.info(
            "Analysis completed: request_id=%s meal_log_id=%s", request.id, log.id
        )
