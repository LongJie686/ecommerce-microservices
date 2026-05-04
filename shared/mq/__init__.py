"""Kafka message queue utilities."""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class KafkaProducer:
    """Async Kafka producer wrapper."""

    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self._bootstrap_servers = bootstrap_servers
        self._producer: Any = None

    async def start(self) -> None:
        from aiokafka import AIOKafkaProducer
        self._producer = AIOKafkaProducer(bootstrap_servers=self._bootstrap_servers)
        await self._producer.start()
        logger.info("Kafka producer started")

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()

    async def send(self, topic: str, data: dict, key: str | None = None) -> None:
        value = json.dumps(data, ensure_ascii=False).encode("utf-8")
        await self._producer.send_and_wait(topic, value, key=key.encode() if key else None)
        logger.debug("Sent to %s: %s", topic, key or "no-key")


class KafkaConsumer:
    """Async Kafka consumer wrapper."""

    def __init__(self, topic: str, group_id: str, bootstrap_servers: str = "localhost:9092"):
        self._topic = topic
        self._group_id = group_id
        self._bootstrap_servers = bootstrap_servers
        self._consumer: Any = None

    async def start(self) -> None:
        from aiokafka import AIOKafkaConsumer
        self._consumer = AIOKafkaConsumer(
            self._topic,
            group_id=self._group_id,
            bootstrap_servers=self._bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )
        await self._consumer.start()
        logger.info("Kafka consumer started: %s / %s", self._topic, self._group_id)

    async def stop(self) -> None:
        if self._consumer:
            await self._consumer.stop()

    async def consume(self):
        async for msg in self._consumer:
            yield msg.value
