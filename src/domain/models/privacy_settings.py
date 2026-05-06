from src.domain.events.base import DomainEvent


class PrivacySettings:
    def __init__(
        self,
        user_id: int,
        analytics_enabled: bool = True,
        crash_reports_enabled: bool = True,
        personalization_enabled: bool = True,
    ):
        self.id: int | None = None
        self.user_id = user_id
        self.analytics_enabled = analytics_enabled
        self.crash_reports_enabled = crash_reports_enabled
        self.personalization_enabled = personalization_enabled
        self.events: list[DomainEvent] = []

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)

    def collect_events(self) -> list[DomainEvent]:
        events, self.events = self.events, []
        return events

    @classmethod
    def create_default(cls, user_id: int) -> "PrivacySettings":
        return cls(user_id=user_id)
