import os
from dotenv import load_dotenv

load_dotenv()

BOT_NAME = "catchjunior"
SPIDER_MODULES = ["catchjunior.spiders"]
NEWSPIDER_MODULE = "catchjunior.spiders"

# 크롤링 에티켓
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 1.5
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# 파이프라인
ITEM_PIPELINES = {
    "catchjunior.pipelines.KafkaPipeline": 300,
}

# Kafka 설정
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_RAW = os.getenv("KAFKA_TOPIC_RAW", "raw-job")

# User-Agent
USER_AGENT = "Mozilla/5.0 (compatible; CatchJuniorBot/1.0)"

# 로그
LOG_LEVEL = "INFO"
