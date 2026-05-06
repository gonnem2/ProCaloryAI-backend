from datetime import datetime

from src.domain.exceptions.user import UserNotFound
from src.domain.models.preferences import Preferences
from src.domain.models.privacy_settings import PrivacySettings
from src.infrastructure.uow import AbstractUnitOfWork


class ProfileService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def get_profile(self, user_id: int) -> dict:
        user = await self.uow.user_repo.get(user_id)
        if not user:
            raise UserNotFound(str(user_id))

        total_records = await self.uow.meal_log_repo.count_by_user(user_id)
        days_in_app = (datetime.now() - user.created_at).days + 1

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at,
            "role": user.role,
            "days_in_app": days_in_app,
            "total_records": total_records,
        }

    async def delete_account(self, user_id: int) -> None:
        user = await self.uow.user_repo.get(user_id)
        if not user:
            raise UserNotFound(str(user_id))
        await self.uow.user_repo.delete(user_id)
        await self.uow.commit()

    async def get_preferences(self, user_id: int) -> dict:
        prefs = await self.uow.preferences_repo.get_by_user(user_id)
        if not prefs:
            prefs = Preferences.create_default(user_id)
            await self.uow.preferences_repo.add(prefs)
            await self.uow.commit()
        return dict(
            diet_type=prefs.diet_type,
            meals_per_day=prefs.meals_per_day,
            water_goal_ml=prefs.water_goal_ml,
            notifications_enabled=prefs.notifications_enabled,
        )

    async def update_preferences(self, user_id: int, **kwargs) -> Preferences:
        prefs = await self.uow.preferences_repo.get_by_user(user_id)
        if not prefs:
            prefs = Preferences.create_default(user_id)
            await self.uow.preferences_repo.add(prefs)
        prefs.update(**kwargs)
        await self.uow.commit()
        return prefs

    async def get_privacy_settings(self, user_id: int) -> dict:
        ps = await self.uow.privacy_repo.get_by_user(user_id)
        if not ps:
            ps = PrivacySettings.create_default(user_id)
            await self.uow.privacy_repo.add(ps)
            await self.uow.commit()
        return dict(
            analytics_enabled=ps.analytics_enabled,
            crash_reports_enabled=ps.crash_reports_enabled,
            personalization_enabled=ps.personalization_enabled,
        )

    async def update_privacy_settings(self, user_id: int, **kwargs) -> PrivacySettings:
        ps = await self.uow.privacy_repo.get_by_user(user_id)
        if not ps:
            ps = PrivacySettings.create_default(user_id)
            await self.uow.privacy_repo.add(ps)
        ps.update(**kwargs)
        await self.uow.commit()
        return ps

    async def get_achievements(self, user_id: int) -> dict:
        user = await self.uow.user_repo.get(user_id)
        if not user:
            raise UserNotFound(str(user_id))

        streak = await self.uow.meal_log_repo.get_streak_days(user_id)
        total_records = await self.uow.meal_log_repo.count_by_user(user_id)
        photo_count = await self.uow.meal_log_repo.count_camera_by_user(user_id)
        goal = await self.uow.goal_repo.get_by_user(user_id)
        days_in_app = (datetime.now() - user.created_at).days + 1

        return {
            "streak_days": streak,
            "goal_created": goal is not None,
            "photos_added": photo_count,
            "days_in_app": days_in_app,
            "total_records": total_records,
        }
