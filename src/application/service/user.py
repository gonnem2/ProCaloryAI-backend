from datetime import datetime, timedelta
from typing import Literal

import jwt

from src.domain.events.user_events import UserLoggedIn, UserRegistered
from src.domain.exceptions.user import InvalidCredentials, UserAlreadyExists
from src.domain.models.user import User
from src.infrastructure.uow import AbstractUnitOfWork
from src.settings import settings

TokenType = Literal["access", "refresh"]

_SECRET = settings.SECRET_JWT_KEY
_ALGORITHM = settings.JWT_ALGORITHM


class UserService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    # --- JWT ---

    @staticmethod
    def _make_token(
        subject: str, token_type: TokenType, expires_delta: timedelta
    ) -> str:
        return jwt.encode(
            {
                "sub": subject,
                "type": token_type,  # ← refresh нельзя использовать как access
                "exp": datetime.now() + expires_delta,
            },
            _SECRET,
            algorithm=_ALGORITHM,
        )

    def create_access_token(self, email: str) -> str:
        return self._make_token(
            email, "access", timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

    def create_refresh_token(self, email: str) -> str:
        return self._make_token(
            email, "refresh", timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

    @staticmethod
    def decode_token(token: str, expected_type: TokenType = "access") -> str:
        """
        Декодирует токен и проверяет его тип.
        Бросает jwt.InvalidTokenError если токен невалиден или тип не совпадает.
        """
        payload = jwt.decode(token, _SECRET, algorithms=[_ALGORITHM])

        if payload.get("type") != expected_type:
            raise jwt.InvalidTokenError(
                f"Expected token type '{expected_type}', got '{payload.get('type')}'"
            )

        return payload["sub"]

    # --- Use Cases ---

    async def create_user(
        self, username: str, password: str, email: str
    ) -> tuple[str, str]:
        async with self.uow as uow:
            existing = await uow.user_repo.get_by_email(email)
            if existing:
                raise UserAlreadyExists(email)

            user = User.create(username=username, email=email, raw_password=password)
            await uow.user_repo.add(user)
            await uow.commit()

            user.events.append(
                UserRegistered(user_id=user.id, email=email, username=username)
            )
            await uow.publish_events()

        return self.create_access_token(email), self.create_refresh_token(email)

    async def login(self, email: str, raw_password: str) -> tuple[str, str]:
        async with self.uow as uow:
            user = await uow.user_repo.get_by_email(email)
            if not user or not user.verify_password(raw_password):
                raise InvalidCredentials()

            user.events.append(UserLoggedIn(user_id=user.id, email=user.email))
            await uow.commit()

        return self.create_access_token(email), self.create_refresh_token(email)

    async def get_user_by_token(self, token: str) -> dict | None:
        try:
            email = self.decode_token(token, expected_type="access")
        except jwt.InvalidTokenError:
            return None

        async with self.uow as uow:
            user = await uow.user_repo.get_by_email(email)

            if not user:
                return None

            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
            }

    async def refresh(self, refresh_token: str) -> tuple[str, str]:
        try:
            email = self.decode_token(refresh_token, expected_type="refresh")
        except jwt.InvalidTokenError:
            raise InvalidCredentials()

        async with self.uow as uow:
            user = await uow.user_repo.get_by_email(email)
            if not user:
                raise InvalidCredentials()

        return self.create_access_token(email), self.create_refresh_token(email)
