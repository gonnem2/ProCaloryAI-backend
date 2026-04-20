from enum import Enum

from src.domain.events.base import DomainEvent
from src.domain.events.user_events import UserPasswordChanged
from src.domain.value_object.password import Password


class UserRoles(Enum):
    user = "user"
    admin = "admin"


class User:
    """Агрегат пользователя"""

    def __init__(
        self,
        username: str,
        password: str,
        email: str,
        role: UserRoles = UserRoles.user,
    ):
        self.id: int | None = None
        self.username = username
        self.email = email
        self.role = role
        self.hashed_password: str = Password.from_raw_password(
            password,
        ).hashed_password
        self.events: list[DomainEvent] = []  # список event'ов

    def collect_events(self) -> list[DomainEvent]:
        """Отдаёт события и очищает накопитель"""
        events, self.events = self.events, []
        return events

    # --- поведение агрегата ---

    def set_password(self, raw_password: str) -> None:
        """Устанавливает пароль через Value Object"""
        self.hashed_password = Password.from_raw_password(raw_password).hashed_password

    def verify_password(self, raw_password: str) -> bool:
        """Проверяет пароль"""
        return Password(self.hashed_password).verify_password(raw_password)

    def change_password(self, raw_password: str) -> None:
        self.set_password(raw_password)
        # агрегат сам знает что произошло что-то важное
        self.events.append(UserPasswordChanged(user_id=self.id, email=self.email))

    @classmethod
    def create(cls, username: str, email: str, raw_password: str) -> "User":
        """Фабричный метод — единственный способ создать пользователя"""
        user = cls(username=username, email=email, password=raw_password)
        return user

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
