from datetime import datetime
from enum import Enum
from src.domain.events.base import DomainEvent


class GoalType(Enum):
    loss = "loss"
    maintain = "maintain"
    gain = "gain"


class Goal:
    def __init__(
        self,
        user_id: int,
        goal_type: GoalType,
        target_kg: float,
        current_weight_kg: float,
        daily_calories: float,
    ):
        self.id: int | None = None
        self.user_id = user_id
        self.goal_type = goal_type
        self.target_kg = target_kg
        self.current_weight_kg = current_weight_kg
        self.daily_calories = daily_calories
        self.created_at = datetime.now()
        self.events: list[DomainEvent] = []

    def calculate_progress(self, total_calorie_deficit: float) -> float:
        """
        Прогресс по формуле: дефицит / 7700 / target_kg * 100
        Дефицит = сумма (daily_calories - фактически съедено) за всё время
        """
        if self.target_kg == 0:
            return 0.0
        kg_changed = total_calorie_deficit / 7700
        return round(min(kg_changed / self.target_kg * 100, 100.0), 2)

    def collect_events(self) -> list[DomainEvent]:
        events, self.events = self.events, []
        return events

    @classmethod
    def create(
        cls,
        user_id: int,
        goal_type: GoalType,
        target_kg: float,
        current_weight_kg: float,
        daily_calories: float,
    ) -> "Goal":
        return cls(
            user_id=user_id,
            goal_type=goal_type,
            target_kg=target_kg,
            current_weight_kg=current_weight_kg,
            daily_calories=daily_calories,
        )
