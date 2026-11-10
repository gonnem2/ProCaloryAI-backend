# src/application/service/meal_log.py
from datetime import date, datetime
from math import isfinite

from src.domain.exceptions.base import DomainException
from src.domain.models.meal_log import MealLog, MealType, MealSource
from src.infrastructure.uow import AbstractUnitOfWork


class MealLogService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def add_meal_log(
        self,
        user_id: int,
        name: str,
        calories: float,
        protein: float,
        fat: float,
        carbs: float,
        meal_type: MealType,
        source: MealSource = MealSource.manual,
        eaten_at: datetime | None = None,
        s3_key: str | None = None,
    ) -> MealLog:
        # FR-3: reject invalid inputs before opening a write operation.
        if not name.strip() or len(name.strip()) > 255:
            raise DomainException("Название должно содержать от 1 до 255 символов")
        if any(not isfinite(v) or v < 0 for v in (calories, protein, fat, carbs)):
            raise DomainException("КБЖУ должны быть конечными неотрицательными числами")
        if isinstance(meal_type, str):
            try:
                meal_type = MealType(meal_type)
            except ValueError:
                raise DomainException("Неизвестный тип приёма пищи")
        if eaten_at is not None and eaten_at.tzinfo is not None:
            from datetime import timezone
            eaten_at = eaten_at.astimezone(timezone.utc).replace(tzinfo=None)
        log = MealLog.create(
            user_id=user_id,
            name=name.strip(),
            calories=calories,
            protein=protein,
            fat=fat,
            carbs=carbs,
            meal_type=meal_type,
            source=source,
            eaten_at=eaten_at,
            s3_key=s3_key,
        )
        await self.uow.meal_log_repo.add(log)
        await self.uow.commit()
        return log

    async def delete_meal_log(self, user_id: int, log_id: int) -> None:
        log = await self.uow.meal_log_repo.get(log_id)
        if not log:
            raise DomainException(f"MealLog {log_id} not found")
        if log.user_id != user_id:
            raise DomainException("Access denied")
        await self.uow.meal_log_repo.delete(log_id)
        await self.uow.commit()

    async def list_by_user(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> list[MealLog]:
        if skip < 0 or not 1 <= limit <= 100:
            raise DomainException("skip должен быть неотрицательным, limit от 1 до 100")
        return await self.uow.meal_log_repo.list_by_user(user_id, skip, limit)

    async def get_today_stats(self, user_id: int) -> dict:
        logs = await self.uow.meal_log_repo.get_by_date(user_id, date.today())
        return {
            "calories": round(sum(l.calories for l in logs), 1),
            "protein": round(sum(l.protein for l in logs), 1),
            "fat": round(sum(l.fat for l in logs), 1),
            "carbs": round(sum(l.carbs for l in logs), 1),
            "count": len(logs),
        }

    async def get_weekly_average(self, user_id: int) -> dict:
        daily = await self.uow.meal_log_repo.get_daily_totals_last_n_days(user_id, 7)
        if not daily:
            return {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
        n = 7
        return {
            "calories": round(sum(d["calories"] for d in daily) / n, 1),
            "protein": round(sum(d["protein"] for d in daily) / n, 1),
            "fat": round(sum(d["fat"] for d in daily) / n, 1),
            "carbs": round(sum(d["carbs"] for d in daily) / n, 1),
        }
