from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.repositories import AbstractRepository


class UserRepository(AbstractRepository):

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session
