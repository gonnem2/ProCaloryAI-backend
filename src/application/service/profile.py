from datetime import datetime

from src.domain.exceptions.user import UserNotFound
from src.domain.models.preferences import Preferences
from src.domain.models.privacy_settings import PrivacySettings
from src.infrastructure.uow import AbstractUnitOfWork


class ProfileService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def get_profile(self, user_id: int) -> dict:
        async with self.uow as uow:
            user = await uow.user_repo.get(user_id)
            if not user:
                raise UserNotFound(str(user_id))

            total_records = await uow.meal_log_repo.count_by_user(user_id)
            days_in_app = (datetime.now() - user.created_at).days + 1

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at,
            "days_in_app": days_in_app,
            "total_records": total_records,
        }

    async def delete_account(self, user_id: int) -> None:
        async with self.uow as uow:
            user = await uow.user_repo.get(user_id)
            if not user:
                raise UserNotFound(str(user_id))
            await uow.user_repo.delete(user_id)
            await uow.commit()

    async def get_preferences(self, user_id: int) -> Preferences:
        async with self.uow as uow:
            prefs = await uow.preferences_repo.get_by_user(user_id)
            if not prefs:
                prefs = Preferences.create_default(user_id)
                await uow.preferences_repo.add(prefs)
                await uow.commit()
        return prefs

    async def update_preferences(self, user_id: int, **kwargs) -> Preferences:
        async with self.uow as uow:
            prefs = await uow.preferences_repo.get_by_user(user_id)
            if not prefs:
                prefs = Preferences.create_default(user_id)
                await uow.preferences_repo.add(prefs)
            prefs.update(**kwargs)
            await uow.commit()
        return prefs

    async def get_privacy_settings(self, user_id: int) -> PrivacySettings:
        async with self.uow as uow:
            ps = await uow.privacy_repo.get_by_user(user_id)
            if not ps:
                ps = PrivacySettings.create_default(user_id)
                await uow.privacy_repo.add(ps)
                await uow.commit()
        return ps

    async def update_privacy_settings(self, user_id: int, **kwargs) -> PrivacySettings:
        async with self.uow as uow:
            ps = await uow.privacy_repo.get_by_user(user_id)
            if not ps:
                ps = PrivacySettings.create_default(user_id)
                await uow.privacy_repo.add(ps)
            ps.update(**kwargs)
            await uow.commit()
        return ps

    async def get_achievements(self, user_id: int) -> dict:
        async with self.uow as uow:
            user = await uow.user_repo.get(user_id)
            if not user:
                raise UserNotFound(str(user_id))

            streak = await uow.meal_log_repo.get_streak_days(user_id)
            total_records = await uow.meal_log_repo.count_by_user(user_id)
            photo_count = await uow.meal_log_repo.count_camera_by_user(user_id)
            goal = await uow.goal_repo.get_by_user(user_id)
            days_in_app = (datetime.now() - user.created_at).days + 1

        return {
            "streak_days": streak,
            "goal_created": goal is not None,
            "photos_added": photo_count,
            "days_in_app": days_in_app,
            "total_records": total_records,
        }
