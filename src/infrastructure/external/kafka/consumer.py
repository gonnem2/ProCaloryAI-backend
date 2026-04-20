import json
import logging
from aiokafka import AIOKafkaConsumer
from src.settings import settings

logger = logging.getLogger(__name__)


async def start_analysis_result_consumer(handle_result):
    """
    Слушает topic photo.analysis.completed
    handle_result(data: dict) — колбэк обработки
    """
    consumer = AIOKafkaConsumer(
        "photo.analysis.completed",
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="backend-analysis-consumer",
        value_deserializer=lambda v: json.loads(v.decode()),
    )
    await consumer.start()
    logger.info("Kafka consumer started: photo.analysis.completed")

    try:
        async for msg in consumer:
            try:
                await handle_result(msg.value)
            except Exception as e:
                logger.exception("Error handling analysis result: %s", e)
    finally:
        await consumer.stop()
