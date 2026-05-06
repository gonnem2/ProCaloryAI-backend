from dataclasses import dataclass
from src.domain.events.base import DomainEvent


@dataclass(frozen=True)
class MealLogAdded(DomainEvent):
    user_id: int = 0
    source: str = "manual"  # "manual" | "camera"


@dataclass(frozen=True)
class MealLogDeleted(DomainEvent):
    user_id: int = 0
    meal_log_id: int = 0


@dataclass(frozen=True)
class GoalCreated(DomainEvent):
    user_id: int = 0


@dataclass(frozen=True)
class PhotoUploadRequested(DomainEvent):
    request_id: int = 0
    user_id: int = 0
    s3_key: str = ""


@dataclass(frozen=True)
class PhotoAnalysisConfirmed(DomainEvent):
    """Фронт подтвердил загрузку — отправляем в AI Core"""

    request_id: int = 0
    user_id: int = 0
    s3_url: str = ""
