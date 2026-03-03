from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models import User
from src.infrastructure.repositories import AbstractRepository


class UserRepository(AbstractRepository[User]):
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session
