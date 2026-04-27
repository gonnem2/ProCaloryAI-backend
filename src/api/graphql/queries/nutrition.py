# src/api/graphql/queries/nutrition.py
import strawberry
from strawberry.types import Info

from src.api.graphql.types import DailyStatsGQL, NutritionGQL, MealLogGQL, DishGQL
from src.application.service.meal_log import MealLogService


@strawberry.type
class NutritionQuery:
    @strawberry.field
    async def daily_stats(self, info: Info, date: str) -> DailyStatsGQL:
        """КБЖУ за день. date: 'YYYY-MM-DD'"""
        user = info.context.get("current_user")
        if not user:
            raise strawberry.exceptions.GraphQLError("Not authenticated")

        service = MealLogService(info.context["uow"])
        logs_with_dishes = await service.get_daily_logs(user_id=user.id, date_str=date)

        meals = []
        total = NutritionGQL(calories=0, protein=0, fat=0, carbs=0)

        for log, dish in logs_with_dishes:
            n = dish.nutrition_for_weight(log.weight_grams)
            total.calories += n.calories
            total.protein += n.protein
            total.fat += n.fat
            total.carbs += n.carbs

            meals.append(
                MealLogGQL(
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
                        calories=n.calories,
                        protein=n.protein,
                        fat=n.fat,
                        carbs=n.carbs,
                    ),
                    eaten_at=log.eaten_at,
                )
            )

        return DailyStatsGQL(date=date, total=total, meals=meals)
