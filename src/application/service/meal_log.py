from datetime import date

from src.domain.exceptions.base import DomainException
from src.domain.models.dish import Dish
from src.domain.models.meal_log import MealLog
from src.infrastructure.uow import AbstractUnitOfWork


class DishNotFound(DomainException):
    def __init__(self, dish_id: int):
        super().__init__(f"Dish with id '{dish_id}' not found")


class MealLogService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def add_meal_log(
        self, user_id: int, dish_id: int, weight_grams: float
    ) -> tuple[MealLog, Dish]:
        async with self.uow as uow:
            dish = await uow.dish_repo.get(dish_id)
            if not dish:
                raise DishNotFound(dish_id)

            log = MealLog.create(
                user_id=user_id,
                dish_id=dish_id,
                weight_grams=weight_grams,
            )
            await uow.meal_log_repo.add(log)
            await uow.commit()

        return log, dish

    async def get_daily_logs(
        self, user_id: int, date_str: str
    ) -> list[tuple[MealLog, Dish]]:
        target_date = date.fromisoformat(date_str)

        async with self.uow as uow:
            return await uow.meal_log_repo.get_by_user_and_date(
                user_id=user_id,
                target_date=target_date,
            )

    async def delete_meal_log(self, user_id: int, log_id: int) -> None:
        async with self.uow as uow:
            log = await uow.meal_log_repo.get(log_id)
            if not log:
                raise DomainException(f"MealLog '{log_id}' not found")
            if log.user_id != user_id:
                raise DomainException("Not allowed")

            await uow.meal_log_repo.delete(log_id)
            await uow.commit()
