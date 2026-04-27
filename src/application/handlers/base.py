import abc
from src.domain.events.base import DomainEvent


class EventHandler[E: DomainEvent](abc.ABC):
    @abc.abstractmethod
    async def handle(self, event: E) -> None:
        raise NotImplementedError
