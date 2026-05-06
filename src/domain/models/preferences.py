from src.domain.events.base import DomainEvent


class Preferences:
    def __init__(
        self,
        user_id: int,
        diet_type: str = "balanced",
        meals_per_day: int = 3,
        water_goal_ml: int = 2000,
        notifications_enabled: bool = True,
    ):
        self.id: int | None = None
        self.user_id = user_id
        self.diet_type = diet_type
        self.meals_per_day = meals_per_day
        self.water_goal_ml = water_goal_ml
        self.notifications_enabled = notifications_enabled
        self.events: list[DomainEvent] = []

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)

    def collect_events(self) -> list[DomainEvent]:
        events, self.events = self.events, []
        return events

    @classmethod
    def create_default(cls, user_id: int) -> "Preferences":
        return cls(user_id=user_id)
