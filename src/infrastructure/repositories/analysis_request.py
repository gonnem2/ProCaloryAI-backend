# src/infrastructure/repositories/analysis_request.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models import AnalysisRequest
from src.infrastructure.repositories import AbstractRepository


class AnalysisRequestRepository(AbstractRepository[AnalysisRequest]):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.seen: set[AnalysisRequest] = set()

    async def get(self, entity_id: int) -> AnalysisRequest | None:
        r = await self.session.get(AnalysisRequest, entity_id)
        if r:
            self.seen.add(r)
        return r

    async def add(self, entity: AnalysisRequest) -> None:
        self.session.add(entity)
        self.seen.add(entity)

    async def update(self, entity: AnalysisRequest) -> None:
        await self.session.merge(entity)
        self.seen.add(entity)

    async def delete(self, entity_id: int) -> None:
        r = await self.get(entity_id)
        if r:
            await self.session.delete(r)

    async def list_by_user(self, user_id: int) -> list[AnalysisRequest]:
        result = await self.session.execute(
            select(AnalysisRequest)
            .where(AnalysisRequest.user_id == user_id)
            .order_by(AnalysisRequest.created_at.desc())
        )
        return list(result.scalars().all())

    async def list(self, skip: int = 0, limit: int = 100) -> list[AnalysisRequest]:
        result = await self.session.execute(
            select(AnalysisRequest).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
