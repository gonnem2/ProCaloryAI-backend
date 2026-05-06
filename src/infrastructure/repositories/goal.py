from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.goal import Goal
from src.infrastructure.repositories import AbstractRepository


class GoalRepository(AbstractRepository[Goal]):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.seen: set[Goal] = set()

    async def get(self, entity_id: int) -> Goal | None:
        goal = await self.session.get(Goal, entity_id)
        if goal:
            self.seen.add(goal)
        return goal

    async def get_by_user(self, user_id: int) -> Goal | None:
        result = await self.session.execute(select(Goal).where(Goal.user_id == user_id))
        goal = result.scalar_one_or_none()
        if goal:
            self.seen.add(goal)
        return goal

    async def add(self, entity: Goal) -> None:
        self.session.add(entity)
        self.seen.add(entity)

    async def update(self, entity: Goal) -> None:
        await self.session.merge(entity)
        self.seen.add(entity)

    async def delete(self, entity_id: int) -> None:
        goal = await self.get(entity_id)
        if goal:
            await self.session.delete(goal)

    async def list(self, skip: int = 0, limit: int = 100) -> list[Goal]:
        result = await self.session.execute(select(Goal).offset(skip).limit(limit))
        return list(result.scalars().all())
