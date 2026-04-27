import abc
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure import repositories
from src.infrastructure.database.db import Session
from src.application.handlers.messagebus import MessageBus, message_bus


class AbstractUnitOfWork(abc.ABC):
    user_repo: repositories.UserRepository

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.rollback()

    async def commit(self) -> None:
        await self._commit()
        await self._publish_events()  # ← после commit, не до!

    async def _publish_events(self) -> None:
        """Собирает события со всех агрегатов и публикует в шину"""
        for (
            entity
        ) in self.user_repo.seen:  # seen - это set из сущностей с которыми мы работали
            events = entity.collect_events()  # тут будет список событий сущности
            await self._bus.handle_all(events)

    async def publish_events(self) -> None:
        """Только публикация — без commit. Для событий после коммита."""
        await self._publish_events()

    @abc.abstractmethod
    async def _commit(self): ...

    @abc.abstractmethod
    async def rollback(self): ...


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(
        self,
        session_factory=Session,
        bus: MessageBus = message_bus,
    ):
        self.session_factory = session_factory
        self._bus = bus

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()
        self.user_repo = repositories.UserRepository(session=self.session)
        self.dish_repo = repositories.DishRepository(session=self.session)
        self.meal_log_repo = repositories.MealLogRepository(session=self.session)
        self.analysis_repo = repositories.AnalysisRequestRepository(
            session=self.session
        )
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
