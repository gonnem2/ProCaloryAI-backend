import strawberry
from strawberry.types import Info

from src.api.graphql.types import (
    UserGQL,
    MealLogGQL,
    NutritionGQL,
    GoalGQL,
    PreferencesGQL,
    PrivacySettingsGQL,
    AchievementsGQL,
)
from src.api.graphql.utils import require_auth, _goal_to_gql, _meal_log_to_gql
from src.application.service.meal_log import MealLogService
from src.application.service.goal import GoalService
from src.application.service.profile import ProfileService


@strawberry.type
class AppQuery:
    @strawberry.field
    async def me(self, info: Info) -> UserGQL:
        user = require_auth(info)
        data = await ProfileService(info.context["uow"]).get_profile(user.id)
        return UserGQL(**data)

    @strawberry.field
    async def meals(
        self, info: Info, skip: int = 0, limit: int = 50
    ) -> list[MealLogGQL]:
        user = require_auth(info)
        logs = await MealLogService(info.context["uow"]).list_by_user(
            user["id"], skip, limit
        )
        return [_meal_log_to_gql(l) for l in logs]

    @strawberry.field
    async def today_stats(self, info: Info) -> NutritionGQL:
        user = require_auth(info)
        stats = await MealLogService(info.context["uow"]).get_today_stats(user.id)
        return NutritionGQL(
            calories=stats["calories"],
            protein=stats["protein"],
            fat=stats["fat"],
            carbs=stats["carbs"],
        )

    @strawberry.field
    async def weekly_average(self, info: Info) -> NutritionGQL:
        user = require_auth(info)
        avg = await MealLogService(info.context["uow"]).get_weekly_average(user.id)
        return NutritionGQL(**avg)

    @strawberry.field
    async def goal(self, info: Info) -> GoalGQL | None:
        user = require_auth(info)
        data = await GoalService(info.context["uow"]).get_goal_with_progress(user.id)
        return _goal_to_gql(data) if data else None

    @strawberry.field
    async def preferences(self, info: Info) -> PreferencesGQL:
        user = require_auth(info)
        prefs = await ProfileService(info.context["uow"]).get_preferences(user.id)
        return PreferencesGQL(**prefs)

    @strawberry.field
    async def privacy_settings(self, info: Info) -> PrivacySettingsGQL:
        user = require_auth(info)
        ps = await ProfileService(info.context["uow"]).get_privacy_settings(user.id)
        return PrivacySettingsGQL(
            **ps,
        )

    @strawberry.field
    async def achievements(self, info: Info) -> AchievementsGQL:
        user = require_auth(info)
        data = await ProfileService(info.context["uow"]).get_achievements(user.id)
        return AchievementsGQL(**data)
