from datetime import datetime
from enum import Enum
from src.domain.events.base import DomainEvent
from src.domain.events.meal_events import MealLogAdded


class MealType(Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"


class MealSource(Enum):
    manual = "manual"
    camera = "camera"


class MealLog:
    def __init__(
        self,
        user_id: int,
        name: str,
        calories: float,
        protein: float,
        fat: float,
        carbs: float,
        meal_type: MealType,
        source: MealSource,
        eaten_at: datetime | None = None,
        s3_key: str | None = None,
    ):
        self.id: int | None = None
        self.user_id = user_id
        self.name = name
        self.calories = calories
        self.protein = protein
        self.fat = fat
        self.carbs = carbs
        self.meal_type = meal_type
        self.source = source
        self.eaten_at = eaten_at or datetime.now()
        self.s3_key = s3_key
        self.events: list[DomainEvent] = []

    def collect_events(self) -> list[DomainEvent]:
        events, self.events = self.events, []
        return events

    @classmethod
    def create(
        cls,
        user_id: int,
        name: str,
        calories: float,
        protein: float,
        fat: float,
        carbs: float,
        meal_type: MealType,
        source: MealSource,
        eaten_at: datetime | None = None,
        s3_key: str | None = None,
    ) -> "MealLog":
        log = cls(
            user_id=user_id,
            name=name,
            calories=calories,
            protein=protein,
            fat=fat,
            carbs=carbs,
            meal_type=meal_type,
            source=source,
            eaten_at=eaten_at,
            s3_key=s3_key,
        )
        log.events.append(MealLogAdded(user_id=user_id, source=source.value))
        return log
