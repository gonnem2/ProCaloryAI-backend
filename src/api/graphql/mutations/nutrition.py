# src/api/graphql/mutations/nutrition.py
import strawberry
from strawberry.types import Info

from src.api.graphql.types import (
    MealLogGQL,
    AddMealLogInput,
    GoalGQL,
    GoalInput,
    PreferencesGQL,
    PreferencesInput,
    PrivacySettingsGQL,
    PrivacySettingsInput,
    UploadUrlGQL,
    AnalysisStatusGQL,
)
from src.api.graphql.utils import (
    handle_domain_errors,
    require_auth,
    _goal_to_gql,
    _meal_log_to_gql,
)
from src.application.service.meal_log import MealLogService
from src.application.service.goal import GoalService
from src.application.service.profile import ProfileService
from src.application.service.analysis import AnalysisService
from src.domain.models.meal_log import MealType, MealSource


@strawberry.type
class NutritionMutation:
    @strawberry.mutation
    async def add_meal_log(self, info: Info, input: AddMealLogInput) -> MealLogGQL:
        user = require_auth(info)
        async with handle_domain_errors():
            log = await MealLogService(info.context["uow"]).add_meal_log(
                user_id=user.id,
                name=input.name,
                calories=input.calories,
                protein=input.protein,
                fat=input.fat,
                carbs=input.carbs,
                meal_type=MealType[input.meal_type],
                source=MealSource.manual,
                eaten_at=input.eaten_at,
            )
        return _meal_log_to_gql(log)

    @strawberry.mutation
    async def delete_meal_log(self, info: Info, log_id: int) -> bool:
        user = require_auth(info)
        async with handle_domain_errors():
            await MealLogService(info.context["uow"]).delete_meal_log(user.id, log_id)
        return True

    @strawberry.mutation
    async def upsert_goal(self, info: Info, input: GoalInput) -> GoalGQL:
        user = require_auth(info)
        from src.domain.models.goal import GoalType

        async with handle_domain_errors():
            result = await GoalService(info.context["uow"]).upsert_goal(
                user_id=user.id,
                goal_type=GoalType[input.goal_type],
                target_kg=input.target_kg,
                current_weight_kg=input.current_weight_kg,
                daily_calories=input.daily_calories,
            )
            # пересчитываем прогресс
            data = await GoalService(info.context["uow"]).get_goal_with_progress(
                user.id
            )
        return _goal_to_gql(data)

    @strawberry.mutation
    async def update_preferences(
        self, info: Info, input: PreferencesInput
    ) -> PreferencesGQL:
        user = require_auth(info)
        async with handle_domain_errors():
            prefs = await ProfileService(info.context["uow"]).update_preferences(
                user_id=user.id,
                diet_type=input.diet_type,
                meals_per_day=input.meals_per_day,
                water_goal_ml=input.water_goal_ml,
                notifications_enabled=input.notifications_enabled,
            )
        return PreferencesGQL(
            diet_type=prefs.diet_type,
            meals_per_day=prefs.meals_per_day,
            water_goal_ml=prefs.water_goal_ml,
            notifications_enabled=prefs.notifications_enabled,
        )

    @strawberry.mutation
    async def update_privacy_settings(
        self, info: Info, input: PrivacySettingsInput
    ) -> PrivacySettingsGQL:
        user = require_auth(info)
        async with handle_domain_errors():
            ps = await ProfileService(info.context["uow"]).update_privacy_settings(
                user_id=user.id,
                analytics_enabled=input.analytics_enabled,
                crash_reports_enabled=input.crash_reports_enabled,
                personalization_enabled=input.personalization_enabled,
            )
        return PrivacySettingsGQL(
            analytics_enabled=ps.analytics_enabled,
            crash_reports_enabled=ps.crash_reports_enabled,
            personalization_enabled=ps.personalization_enabled,
        )

    @strawberry.mutation
    async def request_photo_upload(self, info: Info) -> UploadUrlGQL:
        """Шаг 1: получить presigned URL для загрузки фото напрямую в S3"""
        user = require_auth(info)
        async with handle_domain_errors():
            data = await AnalysisService(info.context["uow"]).request_upload_url(
                user["id"]
            )
        return UploadUrlGQL(**data)

    @strawberry.mutation
    async def confirm_photo_upload(
        self, info: Info, request_id: int
    ) -> AnalysisStatusGQL:
        """Шаг 2: фронт загрузил фото → запускаем анализ"""
        user = require_auth(info)
        async with handle_domain_errors():
            data = await AnalysisService(
                info.context["uow"]
            ).confirm_upload_and_analyze(
                user_id=user["id"],
                request_id=request_id,
            )
        return AnalysisStatusGQL(request_id=data["request_id"], status=data["status"])
