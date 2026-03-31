from src.domain.events.user_events import UserLoggedIn
from src.domain.exceptions.user import InvalidCredentials
from src.infrastructure.uow import AbstractUnitOfWork


class UserService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def create_user(self, username: str, password: str, email: str):
        """Создает пользователя"""
        # проверяем пользователя на уникальность email

        async with self.uow as session:
            session.user_repo

    async def login(self, email: str, raw_password: str) -> tuple[str, str]:
        async with self.uow as uow:
            user = await uow.user_repo.get_by_email(email)
            if not user or not user.verify_password(raw_password):
                raise InvalidCredentials()

            # агрегат фиксирует факт входа
            user.events.append(UserLoggedIn(user_id=user.id, email=user.email))
            await uow.commit()  # ← commit → _publish_events → OnUserLoggedIn

        access = self.create_access_token(email)
        refresh = self.create_refresh_token(email)
        return access, refresh
