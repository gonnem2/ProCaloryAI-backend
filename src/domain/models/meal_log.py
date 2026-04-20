# src/domain/models/meal_log.py
from datetime import datetime
from src.domain.events.base import DomainEvent
from src.domain.events.meal_events import MealLogAdded


class MealLog:
    def __init__(
        self,
        user_id: int,
        dish_id: int,
        weight_grams: float,
        eaten_at: datetime | None = None,
    ):
        self.id: int | None = None
        self.user_id = user_id
        self.dish_id = dish_id
        self.weight_grams = weight_grams
        self.eaten_at = eaten_at or datetime.now()
        self.events: list[DomainEvent] = []

    def collect_events(self) -> list[DomainEvent]:
        events, self.events = self.events, []
        return events

    @classmethod
    def create(cls, user_id: int, dish_id: int, weight_grams: float) -> "MealLog":
        log = cls(user_id=user_id, dish_id=dish_id, weight_grams=weight_grams)
        log.events.append(
            MealLogAdded(user_id=user_id, dish_id=dish_id, weight_grams=weight_grams)
        )
        return log
