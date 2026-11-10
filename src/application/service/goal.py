from math import isfinite
from src.domain.exceptions.base import DomainException
from src.domain.models.goal import Goal, GoalType
from src.infrastructure.uow import AbstractUnitOfWork


class GoalService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def get_goal(self, user_id: int) -> Goal | None:
        return await self.uow.goal_repo.get_by_user(user_id)

    async def upsert_goal(
        self,
        user_id: int,
        goal_type: GoalType,
        target_kg: float,
        current_weight_kg: float,
        daily_calories: float,
    ) -> Goal:
        if isinstance(goal_type, str):
            try:
                goal_type = GoalType(goal_type)
            except ValueError:
                raise DomainException("Неизвестный тип цели")
        if goal_type != GoalType.loss:
            raise DomainException("Пока поддерживается только цель снижения веса")
        if any(not isfinite(v) or v <= 0 for v in (target_kg, current_weight_kg, daily_calories)):
            raise DomainException("Параметры цели должны быть конечными положительными числами")
        if target_kg >= current_weight_kg:
            raise DomainException("Снижение веса должно быть меньше текущего веса")
        existing = await self.uow.goal_repo.get_by_user(user_id)
        if existing:
            existing.goal_type = goal_type
            existing.target_kg = target_kg
            existing.current_weight_kg = current_weight_kg
            existing.daily_calories = daily_calories
            await self.uow.goal_repo.update(existing)
            await self.uow.commit()
            return existing

        goal = Goal.create(
            user_id=user_id,
            goal_type=goal_type,
            target_kg=target_kg,
            current_weight_kg=current_weight_kg,
            daily_calories=daily_calories,
        )
        await self.uow.goal_repo.add(goal)
        await self.uow.commit()
        return goal

    async def get_goal_with_progress(self, user_id: int) -> dict | None:
        goal = await self.uow.goal_repo.get_by_user(user_id)
        if not goal:
            return None

        # считаем суммарный дефицит калорий
        daily_totals = await self.uow.meal_log_repo.get_daily_totals_last_n_days(
            user_id, since=goal.created_at
        )
        total_deficit = sum(goal.daily_calories - d["calories"] for d in daily_totals)
        progress = goal.calculate_progress(total_deficit)

        return {
            "goal": goal,
            "progress_percent": progress,
            "total_calorie_deficit": round(total_deficit, 1),
        }
