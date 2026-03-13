import json
import logging
from datetime import datetime

from kafka import KafkaProducer
from scrapy import Spider

from catchjunior.items import JobPostItem

logger = logging.getLogger(__name__)


class KafkaPipeline:
    producer: KafkaProducer

    def open_spider(self, spider: Spider):
        self.producer = KafkaProducer(
            bootstrap_servers=spider.settings.get("KAFKA_BOOTSTRAP_SERVERS"),
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False, default=str).encode("utf-8"),
        )
        logger.info("Kafka 프로듀서 연결 완료")

    def close_spider(self, spider: Spider):
        self.producer.flush()
        self.producer.close()
        logger.info("Kafka 프로듀서 종료")

    def process_item(self, item: JobPostItem, spider: Spider):
        topic = spider.settings.get("KAFKA_TOPIC_RAW")
        payload = {
            "title": item.get("title"),
            "company": item.get("company"),
            "url": item.get("url"),
            "description": item.get("description"),
            "deadline": item.get("deadline"),
            "source": item.get("source"),
            "techStacks": item.get("tech_stacks", []),
            "collectedAt": item.get("collected_at", datetime.now().isoformat()),
        }
        self.producer.send(topic, value=payload)
        logger.debug("Kafka 발행: %s", item.get("title"))
        return item
