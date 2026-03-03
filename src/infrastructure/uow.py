import abc

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure import repositories
from src.infrastructure.database.db import Session


class AbstractUnitOfWork(abc.ABC):
    user_repo: repositories.AbstractRepository

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.rollback()

    async def commit(self):
        await self._commit()

    @abc.abstractmethod
    async def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """Имплементированный абстрактный UoW"""

    def __init__(self, session_factory=Session):
        self.session_factory = session_factory  # асинхронная сессия

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()
        self.user_repo = repositories.UserRepository(session=self.session)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.session.close()

    async def _commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()


def get_uow() -> AbstractUnitOfWork:
    return SqlAlchemyUnitOfWork()
