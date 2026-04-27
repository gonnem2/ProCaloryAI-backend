# src/domain/events/user_events.py
from dataclasses import dataclass
from src.domain.events.base import DomainEvent


@dataclass(frozen=True)
class UserRegistered(DomainEvent):
    """Пользователь зарегистрировался"""

    user_id: int = 0
    email: str = ""
    username: str = ""


@dataclass(frozen=True)
class UserLoggedIn(DomainEvent):
    """Пользователь вошёл в систему"""

    user_id: int = 0
    email: str = ""


@dataclass(frozen=True)
class UserPasswordChanged(DomainEvent):
    """Пользователь сменил пароль"""

    user_id: int = 0
    email: str = ""
