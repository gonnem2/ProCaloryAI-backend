import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from sqlalchemy import text
import uvicorn

from src.api.graphql.schema import graphql_router
from src.infrastructure.database.db import Session, async_engine
from src.infrastructure.database.orm import start_mappers
from src.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_mappers()
    consumer_task = None
    if settings.PHOTOS_ENABLED:
        from src.application.service.analysis import AnalysisService
        from src.infrastructure.external.kafka.consumer import start_analysis_result_consumer
        from src.infrastructure.external.kafka.producer import kafka_producer
        from src.infrastructure.external.s3.client import s3_client
        from src.infrastructure.uow import SqlAlchemyUnitOfWork

        async def handle_result(data):
            async with SqlAlchemyUnitOfWork() as uow:
                await AnalysisService(uow).handle_analysis_result(data)

        await s3_client.start()
        await kafka_producer.start()
        consumer_task = asyncio.create_task(start_analysis_result_consumer(handle_result))
    try:
        yield
    finally:
        if consumer_task is not None:
            consumer_task.cancel()
            with suppress(asyncio.CancelledError):
                await consumer_task
            await kafka_producer.stop()
            await s3_client.stop()
        await async_engine.dispose()


app = FastAPI(title="ProCaloryAI", lifespan=lifespan)
app.include_router(graphql_router, prefix="/graphql")


@app.get("/health")
async def health():
    async with Session() as session:
        await session.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok", "photos_enabled": settings.PHOTOS_ENABLED}


def main() -> None:
    uvicorn.run("src.main:app", host="0.0.0.0", workers=1)


if __name__ == "__main__":
    main()
