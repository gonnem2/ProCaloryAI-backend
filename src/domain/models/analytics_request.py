# src/domain/models/analysis_request.py
from datetime import datetime
from enum import Enum
from src.domain.events.base import DomainEvent


class AnalysisStatus(Enum):
    pending = "pending"
    uploaded = "uploaded"  # фронт загрузил в S3
    processing = "processing"
    completed = "completed"
    failed = "failed"


class AnalysisRequest:
    def __init__(self, user_id: int, s3_key: str):
        self.id: int | None = None
        self.user_id = user_id
        self.s3_key = s3_key
        self.status = AnalysisStatus.pending
        self.meal_log_id: int | None = None
        self.result: dict | None = None
        self.created_at = datetime.now()
        self.events: list[DomainEvent] = []

    def mark_uploaded(self) -> None:
        """Фронт подтвердил загрузку в S3"""
        self.status = AnalysisStatus.uploaded

    def mark_processing(self) -> None:
        self.status = AnalysisStatus.processing

    def complete(self, meal_log_id: int, result: dict) -> None:
        self.status = AnalysisStatus.completed
        self.meal_log_id = meal_log_id
        self.result = result

    def fail(self) -> None:
        self.status = AnalysisStatus.failed

    def collect_events(self) -> list[DomainEvent]:
        events, self.events = self.events, []
        return events

    @classmethod
    def create(cls, user_id: int, s3_key: str) -> "AnalysisRequest":
        return cls(user_id=user_id, s3_key=s3_key)
