from dataclasses import dataclass
from src.domain.events.base import DomainEvent


@dataclass
class NutritionPer100g:
    """Value Object — КБЖУ на 100г"""

    calories: float
    protein: float
    fat: float
    carbs: float


class Dish:
    def __init__(
        self,
        name: str,
        nutrition: NutritionPer100g,
        created_by_user_id: int,
    ):
        self.id: int | None = None
        self.name = name
        self.calories_per_100g = nutrition.calories
        self.protein_per_100g = nutrition.protein
        self.fat_per_100g = nutrition.fat
        self.carbs_per_100g = nutrition.carbs
        self.created_by_user_id = created_by_user_id
        self.events: list[DomainEvent] = []

    def nutrition_for_weight(self, grams: float) -> NutritionPer100g:
        """КБЖУ для конкретного веса"""
        k = grams / 100
        return NutritionPer100g(
            calories=round(self.calories_per_100g * k, 1),
            protein=round(self.protein_per_100g * k, 1),
            fat=round(self.fat_per_100g * k, 1),
            carbs=round(self.carbs_per_100g * k, 1),
        )

    def collect_events(self) -> list[DomainEvent]:
        events, self.events = self.events, []
        return events

    @classmethod
    def create(cls, name: str, nutrition: NutritionPer100g, user_id: int) -> "Dish":
        return cls(name=name, nutrition=nutrition, created_by_user_id=user_id)
