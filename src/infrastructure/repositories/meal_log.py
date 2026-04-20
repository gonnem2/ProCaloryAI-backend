# src/infrastructure/repositories/meal_log.py
from datetime import date, datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.dish import Dish
from src.domain.models.meal_log import MealLog
from src.infrastructure.repositories import AbstractRepository


class MealLogRepository(AbstractRepository[MealLog]):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.seen: set[MealLog] = set()

    async def get(self, entity_id: int) -> MealLog | None:
        log = await self.session.get(MealLog, entity_id)
        if log:
            self.seen.add(log)
        return log

    async def add(self, entity: MealLog) -> None:
        self.session.add(entity)
        self.seen.add(entity)

    async def update(self, entity: MealLog) -> None:
        await self.session.merge(entity)
        self.seen.add(entity)

    async def delete(self, entity_id: int) -> None:
        log = await self.get(entity_id)
        if log:
            await self.session.delete(log)

    async def list(self, skip: int = 0, limit: int = 100) -> list[MealLog]:
        result = await self.session.execute(select(MealLog).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_user_and_date(
        self, user_id: int, target_date: date
    ) -> list[tuple[MealLog, Dish]]:
        """
        Возвращает все записи пользователя за день вместе с блюдом.
        JOIN делаем на уровне запроса — не тащим N+1.
        """
        day_start = datetime.combine(target_date, datetime.min.time())
        day_end = datetime.combine(target_date, datetime.max.time())

        result = await self.session.execute(
            select(MealLog, Dish)
            .join(Dish, MealLog.dish_id == Dish.id)
            .where(
                and_(
                    MealLog.user_id == user_id,
                    MealLog.eaten_at >= day_start,
                    MealLog.eaten_at <= day_end,
                )
            )
            .order_by(MealLog.eaten_at)
        )
        rows = result.all()

        for log, dish in rows:
            self.seen.add(log)

        return [(log, dish) for log, dish in rows]
