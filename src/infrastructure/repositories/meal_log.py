from datetime import date, datetime, timedelta
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

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


    async def list_by_user(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> list[MealLog]:
        result = await self.session.execute(
            select(MealLog)
            .where(MealLog.user_id == user_id)
            .order_by(MealLog.eaten_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_date(self, user_id: int, target_date: date) -> list[MealLog]:
        day_start = datetime.combine(target_date, datetime.min.time())
        day_end = datetime.combine(target_date, datetime.max.time())
        result = await self.session.execute(
            select(MealLog)
            .where(
                and_(
                    MealLog.user_id == user_id,
                    MealLog.eaten_at >= day_start,
                    MealLog.eaten_at <= day_end,
                )
            )
            .order_by(MealLog.eaten_at)
        )
        return list(result.scalars().all())

    async def get_daily_totals_last_n_days(
        self, user_id: int, days: int = 7, since: datetime | None = None
    ) -> list[dict]:
        from sqlalchemy import cast, Date

        today = date.today()
        start = since or datetime.combine(today - timedelta(days=days - 1), datetime.min.time())
        end = datetime.combine(today + timedelta(days=1), datetime.min.time())
        result = await self.session.execute(
            select(
                cast(MealLog.eaten_at, Date).label("day"),
                func.sum(MealLog.calories).label("calories"),
                func.sum(MealLog.protein).label("protein"),
                func.sum(MealLog.fat).label("fat"),
                func.sum(MealLog.carbs).label("carbs"),
            )
            .where(MealLog.user_id == user_id, MealLog.eaten_at >= start, MealLog.eaten_at < end)
            .group_by(cast(MealLog.eaten_at, Date))
            .order_by(cast(MealLog.eaten_at, Date))
        )
        return [dict(day=str(r.day), calories=r.calories or 0, protein=r.protein or 0,
                     fat=r.fat or 0, carbs=r.carbs or 0) for r in result.all()]

    async def count_by_user(self, user_id: int) -> int:
        result = await self.session.execute(
            select(func.count()).where(MealLog.user_id == user_id)
        )
        return result.scalar_one()

    async def count_camera_by_user(self, user_id: int) -> int:
        from src.domain.models.meal_log import MealSource

        result = await self.session.execute(
            select(func.count()).where(
                and_(MealLog.user_id == user_id, MealLog.source == MealSource.camera)
            )
        )
        return result.scalar_one()

    async def get_streak_days(self, user_id: int) -> int:
        """Сколько дней подряд пользователь добавляет записи"""
        from sqlalchemy import cast, Date

        result = await self.session.execute(
            select(func.count(func.distinct(cast(MealLog.eaten_at, Date)))).where(
                MealLog.user_id == user_id
            )
        )
        # Упрощённая версия — считаем подряд идущие дни назад от сегодня
        days_result = await self.session.execute(
            select(cast(MealLog.eaten_at, Date).label("day"))
            .where(MealLog.user_id == user_id)
            .group_by(cast(MealLog.eaten_at, Date))
            .order_by(cast(MealLog.eaten_at, Date).desc())
        )
        days = [row.day for row in days_result.all()]
        if not days:
            return 0
        streak = 0
        today = date.today()
        for i, d in enumerate(days):
            expected = today - __import__("datetime").timedelta(days=i)
            if d == expected:
                streak += 1
            else:
                break
        return streak


    async def list(self, skip: int = 0, limit: int = 100) -> list[MealLog]:
        result = await self.session.execute(select(MealLog).offset(skip).limit(limit))
        return list(result.scalars().all())
