from typing import Callable, Awaitable, Type
from src.domain.events.base import DomainEvent

# тип хендлера
Handler = Callable[[DomainEvent], Awaitable[None]]


class MessageBus:
    """
    Синхронная in-process шина событий.
    Одно событие → один или несколько хендлеров.

    Если вкратце, то мы тут создаем словарь, где ключ -
    это некий ивент, а значение - список хендлеров(функций),
    куда этот ивент будет передан

    Штука используется в конце UoW

    Вообще по-хорощему эту штуку через кафку и сторонние сервисы реализовать, но пока - это приятная
    Абстракция для наших целей
    """

    def __init__(self):
        self._handlers: dict[Type[DomainEvent], list[Handler]] = {}

    def register(self, event_type: Type[DomainEvent], handler: Handler) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    async def handle(self, event: DomainEvent) -> None:
        # ну т.е. по-хорошему тут будет вызов кафки и отправка сообщения в топик
        handlers = self._handlers.get(type(event), [])
        for handler in handlers:
            # ну вот буквально проходимся по функциям и передаем туда ключ(событие)
            await handler(event)

    async def handle_all(self, events: list[DomainEvent]) -> None:
        for event in events:
            await self.handle(event)


# --- wiring: регистрируем хендлеры ---

from src.application.handlers.user_handler import (
    OnUserRegistered,
    OnUserLoggedIn,
    OnUserPasswordChanged,
)
from src.domain.events.user_events import (
    UserRegistered,
    UserLoggedIn,
    UserPasswordChanged,
)


def create_message_bus() -> MessageBus:
    bus = MessageBus()
    bus.register(UserRegistered, OnUserRegistered().handle)
    bus.register(UserLoggedIn, OnUserLoggedIn().handle)
    bus.register(UserPasswordChanged, OnUserPasswordChanged().handle)
    return bus


# синглтон шины
message_bus = create_message_bus()
