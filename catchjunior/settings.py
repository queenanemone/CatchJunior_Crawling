import os
from dotenv import load_dotenv

load_dotenv()

BOT_NAME = "catchjunior"
SPIDER_MODULES = ["catchjunior.spiders"]
NEWSPIDER_MODULE = "catchjunior.spiders"

# 크롤링 에티켓
ROBOTSTXT_OBEY = False  # API 기반 스파이더는 robots.txt 무관, HTML 스파이더는 spider 레벨에서 관리
DOWNLOAD_DELAY = 1.5
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# AutoThrottle — 서버 부하에 따라 딜레이 자동 조절
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 10.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# 기본 요청 헤더
DEFAULT_REQUEST_HEADERS = {
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}

# 파이프라인
ITEM_PIPELINES = {
    "catchjunior.pipelines.KafkaPipeline": 300,
}

# Kafka 설정
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_RAW = os.getenv("KAFKA_TOPIC_RAW", "raw-job")

# 사람인 Open API access-key (발급 후 .env에 설정)
SARAMIN_ACCESS_KEY = os.getenv("SARAMIN_ACCESS_KEY", "")

# 로그
LOG_LEVEL = "INFO"
