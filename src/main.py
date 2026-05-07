import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from src.api.graphql.schema import graphql_router
from src.application.service.analysis import AnalysisService
from src.infrastructure.database.orm import start_mappers
from src.infrastructure.external.kafka.consumer import start_analysis_result_consumer
from src.infrastructure.external.kafka.producer import kafka_producer
from src.infrastructure.external.s3.client import s3_client
from src.infrastructure.uow import SqlAlchemyUnitOfWork


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_mappers()
    await kafka_producer.start()

    # запускаем consumer в фоне
    uow = SqlAlchemyUnitOfWork()
    service = AnalysisService(uow)
    consumer_task = asyncio.create_task(
        start_analysis_result_consumer(service.handle_analysis_result)
    )
    await s3_client.start()
    yield
    await s3_client.stop()
    consumer_task.cancel()
    await kafka_producer.stop()


app = FastAPI(lifespan=lifespan)

app.include_router(graphql_router, prefix="/graphql")


def main() -> None:
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        workers=1,
    )


if __name__ == "__main__":
    main()
