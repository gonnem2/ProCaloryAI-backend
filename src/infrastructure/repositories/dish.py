from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.dish import Dish
from src.infrastructure.repositories import AbstractRepository


class DishRepository(AbstractRepository[Dish]):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.seen: set[Dish] = set()

    async def get(self, entity_id: int) -> Dish | None:
        dish = await self.session.get(Dish, entity_id)
        if dish:
            self.seen.add(dish)
        return dish

    async def get_by_name(self, name: str) -> Dish | None:
        result = await self.session.execute(select(Dish).where(Dish.name == name))
        dish = result.scalar_one_or_none()
        if dish:
            self.seen.add(dish)
        return dish

    async def add(self, entity: Dish) -> None:
        self.session.add(entity)
        self.seen.add(entity)

    async def update(self, entity: Dish) -> None:
        await self.session.merge(entity)
        self.seen.add(entity)

    async def delete(self, entity_id: int) -> None:
        dish = await self.get(entity_id)
        if dish:
            await self.session.delete(dish)

    async def list(self, skip: int = 0, limit: int = 100) -> list[Dish]:
        result = await self.session.execute(select(Dish).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def list_by_user(self, user_id: int) -> list[Dish]:
        result = await self.session.execute(
            select(Dish).where(Dish.created_by_user_id == user_id)
        )
        return list(result.scalars().all())
