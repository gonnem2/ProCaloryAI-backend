import abc
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure import repositories
from src.infrastructure.database.db import Session
from src.application.handlers.messagebus import MessageBus, message_bus


class AbstractUnitOfWork(abc.ABC):
    user_repo: repositories.UserRepository
    meal_log_repo: repositories.MealLogRepository
    goal_repo: repositories.GoalRepository
    preferences_repo: repositories.PreferencesRepository
    privacy_repo: repositories.PrivacySettingsRepository
    analysis_repo: repositories.AnalysisRequestRepository

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.rollback()

    async def commit(self) -> None:
        await self._commit()
        await self._publish_events()

    async def publish_events(self) -> None:
        await self._publish_events()

    async def _publish_events(self) -> None:
        all_seen = [
            *self.user_repo.seen,
            *self.meal_log_repo.seen,
            *self.goal_repo.seen,
            *self.preferences_repo.seen,
            *self.privacy_repo.seen,
            *self.analysis_repo.seen,
        ]
        for entity in all_seen:
            events = entity.collect_events()
            await self._bus.handle_all(events)

    @abc.abstractmethod
    async def _commit(self): ...

    @abc.abstractmethod
    async def rollback(self): ...


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=Session, bus: MessageBus = message_bus):
        self.session_factory = session_factory
        self._bus = bus

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()
        self.user_repo = repositories.UserRepository(session=self.session)
        self.meal_log_repo = repositories.MealLogRepository(session=self.session)
        self.goal_repo = repositories.GoalRepository(session=self.session)
        self.preferences_repo = repositories.PreferencesRepository(session=self.session)
        self.privacy_repo = repositories.PrivacySettingsRepository(session=self.session)
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


async def get_uow() -> AbstractUnitOfWork:
    async with SqlAlchemyUnitOfWork() as uow:
        yield uow
