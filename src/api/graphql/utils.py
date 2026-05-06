# src/api/graphql/utils.py
from contextlib import asynccontextmanager
from strawberry.types import Info
import strawberry

from src.domain.exceptions.base import DomainException
from src.domain.models.meal_log import MealLog
from src.api.graphql.types import MealLogGQL, NutritionGQL, GoalGQL


@asynccontextmanager
async def handle_domain_errors():
    try:
        yield
    except DomainException as e:
        raise strawberry.exceptions.GraphQLError(str(e))


def require_auth(info: Info):
    user = info.context.get("current_user")
    if not user:
        raise strawberry.exceptions.GraphQLError("Not authenticated")
    return user


def _meal_log_to_gql(log: MealLog) -> MealLogGQL:
    return MealLogGQL(
        id=log.id,
        name=log.name,
        nutrition=NutritionGQL(
            calories=log.calories,
            protein=log.protein,
            fat=log.fat,
            carbs=log.carbs,
        ),
        meal_type=log.meal_type.value,
        source=log.source.value,
        eaten_at=log.eaten_at,
        s3_key=log.s3_key,
    )


def _goal_to_gql(data: dict) -> GoalGQL:
    goal = data["goal"]
    return GoalGQL(
        id=goal.id,
        goal_type=goal.goal_type.value,
        target_kg=goal.target_kg,
        current_weight_kg=goal.current_weight_kg,
        daily_calories=goal.daily_calories,
        progress_percent=data["progress_percent"],
        total_calorie_deficit=data["total_calorie_deficit"],
        created_at=goal.created_at,
    )
