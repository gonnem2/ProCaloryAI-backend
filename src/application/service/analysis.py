import uuid
import logging

from src.domain.models import AnalysisRequest
from src.infrastructure.external.kafka.producer import kafka_producer
from src.infrastructure.external.s3.client import s3_client
from src.infrastructure.uow import AbstractUnitOfWork

logger = logging.getLogger(__name__)


class AnalysisService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def request_upload_url(self, user_id: int) -> dict:
        """
        Шаг 1: создаём AnalysisRequest, генерируем presigned PUT URL для Android.
        Android загружает фото напрямую в MinIO через nginx по этому URL.
        """
        s3_key = f"photos/{user_id}/{uuid.uuid4()}.jpg"

        # Публичный presigned URL — подпись считается для public_url
        # чтобы Android мог отправить PUT напрямую
        upload_url = await s3_client.get_presigned_upload_url(
            key=s3_key,
            expires_in=300,
        )

        async with self.uow as uow:
            request = AnalysisRequest.create(user_id=user_id, s3_key=s3_key)
            await uow.analysis_repo.add(request)
            await uow.commit()

        return {
            "request_id": request.id,
            "upload_url": upload_url,  # http://10.0.2.2/storage/photos/...
            "s3_key": s3_key,
            "expires_in": 300,
        }

    async def confirm_upload_and_analyze(self, user_id: int, request_id: int) -> dict:
        """
        Шаг 2: Android подтверждает загрузку → отправляем задачу в Kafka.
        AI Core получит публичный URL чтобы скачать фото из Colab.
        """
        async with self.uow as uow:
            request = await uow.analysis_repo.get(request_id)
            if not request or request.user_id != user_id:
                raise ValueError("Analysis request not found")

            request.mark_uploaded()
            request.mark_processing()
            await uow.commit()

        # Публичный URL для AI Core (Colab) — не presigned, просто ссылка
        # AI Core скачает фото по этому URL для анализа
        public_s3_url = await s3_client.get_internal_presigned_url(request.s3_key)

        await kafka_producer.send(
            "photo.analysis.requested",
            {
                "request_id": request.id,
                "user_id": user_id,
                "s3_url": public_s3_url,  # http://10.0.2.2/storage/photos/...
            },
        )

        logger.info(
            "Analysis requested: request_id=%s user_id=%s s3_url=%s",
            request.id,
            user_id,
            public_s3_url,
        )
        return {"request_id": request.id, "status": "processing"}

    async def handle_analysis_result(self, data: dict) -> None:
        """
        Колбэк Kafka consumer — сохраняем результат в AnalysisRequest.
        MealLog НЕ создаём — пользователь сам подтвердит через addMealLog().
        """
        async with self.uow as uow:
            request = await uow.analysis_repo.get(data["request_id"])
            if not request:
                logger.warning("Unknown request_id: %s", data["request_id"])
                return

            # Сохраняем только результат — без создания MealLog
            request.complete(
                meal_log_id=None,  # ← не привязываем к MealLog
                result={
                    "dish_name": data.get("dish_name", ""),
                    "calories": data.get("calories", 0),
                    "protein": data.get("protein", 0),
                    "fat": data.get("fat", 0),
                    "carbs": data.get("carbs", 0),
                },
            )
            await uow.commit()

        logger.info("Analysis result saved: request_id=%s", data["request_id"])

    # async def handle_analysis_result(self, data: dict) -> None:
    #     """
    #     Колбэк Kafka consumer — приходит результат от AI Core.
    #     data: {request_id, dish_name, calories, protein, fat, carbs}
    #     """
    #     async with self.uow as uow:
    #         request = await uow.analysis_repo.get(data["request_id"])
    #         if not request:
    #             logger.warning("Unknown request_id: %s", data["request_id"])
    #             return
    #
    #         log = MealLog.create(
    #             user_id=request.user_id,
    #             name=data["dish_name"],
    #             calories=data["calories"],
    #             protein=data["protein"],
    #             fat=data["fat"],
    #             carbs=data["carbs"],
    #             meal_type=MealType.snack,
    #             source=MealSource.camera,
    #             s3_key=request.s3_key,
    #         )
    #         await uow.meal_log_repo.add(log)
    #         await uow.commit()
    #
    #         request.complete(meal_log_id=log.id, result=data)
    #         await uow.commit()
    #
    #     logger.info(
    #         "Analysis completed: request_id=%s meal_log_id=%s",
    #         request.id,
    #         log.id,
    #     )
