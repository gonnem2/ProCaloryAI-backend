from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.user import User
from src.infrastructure.repositories import AbstractRepository


class UserRepository(AbstractRepository[User]):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.seen: set[User] = set()   # ← все агрегаты, с которыми работали

    async def get(self, entity_id: int) -> User | None:
        user = await self.session.get(User, entity_id)
        if user:
            self.seen.add(user)
        return user

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        if user:
            self.seen.add(user)
        return user

    async def add(self, entity: User) -> None:
        self.session.add(entity)
        self.seen.add(entity)

    async def update(self, entity: User) -> None:
        await self.session.merge(entity)
        self.seen.add(entity)

    async def delete(self, entity_id: int) -> None:
        user = await self.get(entity_id)
        if user:
            await self.session.delete(user)

    async def list(self, skip: int = 0, limit: int = 100) -> list[User]:
        result = await self.session.execute(
            select(User).offset(skip).limit(limit)
        )
        return list(result.scalars().all())