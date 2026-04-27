from dataclasses import dataclass
from src.domain.events.base import DomainEvent


@dataclass(frozen=True)
class MealLogAdded(DomainEvent):
    user_id: int = 0
    dish_id: int = 0
    weight_grams: float = 0.0


@dataclass(frozen=True)
class PhotoUploadedForAnalysis(DomainEvent):
    """Публикуется в Kafka → AI Core"""

    request_id: int = 0
    user_id: int = 0
    s3_url: str = ""


@dataclass(frozen=True)
class AnalysisCompleted(DomainEvent):
    """Приходит из Kafka от AI Core"""

    request_id: int = 0
    dish_name: str = ""
    calories_per_100g: float = 0.0
    protein_per_100g: float = 0.0
    fat_per_100g: float = 0.0
    carbs_per_100g: float = 0.0
