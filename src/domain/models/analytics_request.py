from datetime import datetime
from enum import Enum


class AnalysisStatus(Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class AnalysisRequest:
    def __init__(self, user_id: int, s3_key: str):
        self.id: int | None = None
        self.user_id = user_id
        self.s3_key = s3_key
        self.status = AnalysisStatus.pending
        self.dish_id: int | None = None
        self.created_at = datetime.now()
        self.events = []

    def complete(self, dish_id: int) -> None:
        self.status = AnalysisStatus.completed
        self.dish_id = dish_id

    def fail(self) -> None:
        self.status = AnalysisStatus.failed

    def collect_events(self) -> list:
        events, self.events = self.events, []
        return events

    @classmethod
    def create(cls, user_id: int, s3_key: str) -> "AnalysisRequest":
        return cls(user_id=user_id, s3_key=s3_key)
