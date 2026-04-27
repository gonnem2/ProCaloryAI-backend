# src/infrastructure/kafka/producer.py
import json
from aiokafka import AIOKafkaProducer
from src.settings import settings


class KafkaEventProducer:
    def __init__(self):
        self._producer: AIOKafkaProducer | None = None

    async def start(self):
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode(),
        )
        await self._producer.start()

    async def stop(self):
        if self._producer:
            await self._producer.stop()

    async def send(self, topic: str, payload: dict) -> None:
        await self._producer.send_and_wait(topic, payload)


kafka_producer = KafkaEventProducer()
