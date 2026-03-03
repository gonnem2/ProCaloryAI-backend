from src.infrastructure.uow import AbstractUnitOfWork


class UserService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def create_user(self, username: str, password: str, email: str):
        """Создает пользователя"""
        # проверяем пользователя на уникальность email

        async with self.uow as session:
            session.user_repo