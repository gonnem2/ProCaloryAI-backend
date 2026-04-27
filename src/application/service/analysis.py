import base64

from src.domain.models import AnalysisRequest, NutritionPer100g, MealLog, Dish
from src.infrastructure.external.kafka.producer import kafka_producer
from src.infrastructure.external.s3.client import s3_client
from src.infrastructure.uow import AbstractUnitOfWork


class AnalysisService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def request_analysis(self, user_id: int, photo_base64: str) -> int:
        """
        1. Декодирует base64
        2. Загружает в S3
        3. Сохраняет AnalysisRequest
        4. Публикует в Kafka
        Возвращает request_id
        """
        photo_bytes = base64.b64decode(photo_base64)
        s3_key = await s3_client.upload_photo(photo_bytes)
        s3_url = s3_client.get_url(s3_key)

        async with self.uow as uow:
            request = AnalysisRequest.create(user_id=user_id, s3_key=s3_key)
            await uow.analysis_repo.add(request)
            await uow.commit()

        await kafka_producer.send(
            "photo.analysis.requested",
            {
                "request_id": request.id,
                "user_id": user_id,
                "s3_url": s3_url,
            },
        )

        return request.id

    async def handle_analysis_result(self, data: dict) -> None:
        """
        Колбэк Kafka consumer — создаёт Dish + MealLog
        data: {request_id, dish_name, calories, protein, fat, carbs}
        """
        async with self.uow as uow:
            analysis_req = await uow.analysis_repo.get(data["request_id"])
            if not analysis_req:
                return

            nutrition = NutritionPer100g(
                calories=data["calories_per_100g"],
                protein=data["protein_per_100g"],
                fat=data["fat_per_100g"],
                carbs=data["carbs_per_100g"],
            )
            dish = Dish.create(
                name=data["dish_name"],
                nutrition=nutrition,
                user_id=analysis_req.user_id,
            )
            await uow.dish_repo.add(dish)
            await uow.commit()

            # по умолчанию логируем 100г
            meal_log = MealLog.create(
                user_id=analysis_req.user_id,
                dish_id=dish.id,
                weight_grams=100.0,
            )
            await uow.meal_log_repo.add(meal_log)

            analysis_req.complete(dish_id=dish.id)
            await uow.commit()
