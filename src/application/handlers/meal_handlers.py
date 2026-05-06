import logging
from src.domain.events.meal_events import (
    MealLogAdded,
    MealLogDeleted,
    GoalCreated,
    PhotoUploadRequested,
    PhotoAnalysisConfirmed,
)

logger = logging.getLogger(__name__)


class OnMealLogAdded:
    async def handle(self, event: MealLogAdded) -> None:
        logger.info(
            "Meal added: user_id=%s source=%s",
            event.user_id,
            event.source,
        )
        # Здесь можно:
        # - обновить streak в Redis
        # - проверить достижения (первая запись, 100-я запись и т.д.)
        # - пересчитать прогресс цели
        # await achievement_service.check(event.user_id)


class OnMealLogDeleted:
    async def handle(self, event: MealLogDeleted) -> None:
        logger.info(
            "Meal deleted: user_id=%s log_id=%s",
            event.user_id,
            event.meal_log_id,
        )
        # await streak_service.recalculate(event.user_id)


class OnGoalCreated:
    async def handle(self, event: GoalCreated) -> None:
        logger.info("Goal created: user_id=%s", event.user_id)
        # await notification_service.send(
        #     user_id=event.user_id,
        #     message="Цель установлена! Начнём отслеживать прогресс.",
        # )


class OnPhotoUploadRequested:
    """
    Фронт запросил presigned URL — фото ещё не загружено.
    Можно логировать или инициализировать таймер ожидания.
    """

    async def handle(self, event: PhotoUploadRequested) -> None:
        logger.info(
            "Photo upload requested: request_id=%s user_id=%s key=%s",
            event.request_id,
            event.user_id,
            event.s3_key,
        )


class OnPhotoAnalysisConfirmed:
    """
    Фронт подтвердил загрузку — задача ушла в Kafka на AI Core.
    Можно отправить пуш: «Фото получено, анализируем...»
    """

    async def handle(self, event: PhotoAnalysisConfirmed) -> None:
        logger.info(
            "Photo confirmed, sent to AI Core: request_id=%s user_id=%s",
            event.request_id,
            event.user_id,
        )
        # await push_service.send(
        #     user_id=event.user_id,
        #     title="Анализируем фото",
        #     body="Обычно это занимает несколько секунд",
        # )
