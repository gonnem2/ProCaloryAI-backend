from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.preferences import Preferences
from src.domain.models.privacy_settings import PrivacySettings
from src.infrastructure.repositories import AbstractRepository


class PreferencesRepository(AbstractRepository[Preferences]):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.seen: set[Preferences] = set()

    async def get(self, entity_id: int) -> Preferences | None:
        p = await self.session.get(Preferences, entity_id)
        if p:
            self.seen.add(p)
        return p

    async def get_by_user(self, user_id: int) -> Preferences | None:
        result = await self.session.execute(
            select(Preferences).where(Preferences.user_id == user_id)
        )
        p = result.scalar_one_or_none()
        if p:
            self.seen.add(p)
        return p

    async def add(self, entity: Preferences) -> None:
        self.session.add(entity)
        self.seen.add(entity)

    async def update(self, entity: Preferences) -> None:
        await self.session.merge(entity)
        self.seen.add(entity)

    async def delete(self, entity_id: int) -> None:
        p = await self.get(entity_id)
        if p:
            await self.session.delete(p)

    async def list(self, skip: int = 0, limit: int = 100) -> list[Preferences]:
        result = await self.session.execute(
            select(Preferences).offset(skip).limit(limit)
        )
        return list(result.scalars().all())


class PrivacySettingsRepository(AbstractRepository[PrivacySettings]):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.seen: set[PrivacySettings] = set()

    async def get(self, entity_id: int) -> PrivacySettings | None:
        p = await self.session.get(PrivacySettings, entity_id)
        if p:
            self.seen.add(p)
        return p

    async def get_by_user(self, user_id: int) -> PrivacySettings | None:
        result = await self.session.execute(
            select(PrivacySettings).where(PrivacySettings.user_id == user_id)
        )
        p = result.scalar_one_or_none()
        if p:
            self.seen.add(p)
        return p

    async def add(self, entity: PrivacySettings) -> None:
        self.session.add(entity)
        self.seen.add(entity)

    async def update(self, entity: PrivacySettings) -> None:
        await self.session.merge(entity)
        self.seen.add(entity)

    async def delete(self, entity_id: int) -> None:
        p = await self.get(entity_id)
        if p:
            await self.session.delete(p)

    async def list(self, skip: int = 0, limit: int = 100) -> list[PrivacySettings]:
        result = await self.session.execute(
            select(PrivacySettings).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
