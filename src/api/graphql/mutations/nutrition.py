# src/api/graphql/mutations/nutrition.py
import strawberry
from strawberry.types import Info

from src.api.graphql.types import (
    AnalysisRequestGQL,
    MealLogGQL,
    NutritionGQL,
    DishGQL,
    AnalyzePhotoInput,
    AddMealLogInput,
)
from src.api.graphql.utils import handle_domain_errors
from src.application.service.analysis import AnalysisService
from src.application.service.meal_log import MealLogService


@strawberry.type
class NutritionMutation:
    @strawberry.mutation
    async def analyze_photo(
        self, info: Info, input: AnalyzePhotoInput
    ) -> AnalysisRequestGQL:
        """Отправляет фото на анализ, возвращает request_id для поллинга"""
        user = info.context.get("current_user")
        if not user:
            raise strawberry.exceptions.GraphQLError("Not authenticated")

        async with handle_domain_errors():
            service = AnalysisService(info.context["uow"])
            request_id = await service.request_analysis(
                user_id=user.id,
                photo_base64=input.photo_base64,
            )

        return AnalysisRequestGQL(request_id=request_id)

    @strawberry.mutation
    async def add_meal_log(self, info: Info, input: AddMealLogInput) -> MealLogGQL:
        """Вручную добавить блюдо в дневник"""
        user = info.context.get("current_user")
        if not user:
            raise strawberry.exceptions.GraphQLError("Not authenticated")

        async with handle_domain_errors():
            service = MealLogService(info.context["uow"])
            log, dish = await service.add_meal_log(
                user_id=user.id,
                dish_id=input.dish_id,
                weight_grams=input.weight_grams,
            )

        nutrition = dish.nutrition_for_weight(log.weight_grams)
        return MealLogGQL(
            id=log.id,
            dish=DishGQL(
                id=dish.id,
                name=dish.name,
                nutrition_per_100g=NutritionGQL(
                    calories=dish.calories_per_100g,
                    protein=dish.protein_per_100g,
                    fat=dish.fat_per_100g,
                    carbs=dish.carbs_per_100g,
                ),
            ),
            weight_grams=log.weight_grams,
            nutrition_total=NutritionGQL(
                calories=nutrition.calories,
                protein=nutrition.protein,
                fat=nutrition.fat,
                carbs=nutrition.carbs,
            ),
            eaten_at=log.eaten_at,
        )
