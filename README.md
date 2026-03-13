# CatchJunior Crawling

캐치주니어의 채용 공고 크롤러. 원티드·사람인 등 주요 채용 사이트에서 신입 공고를 수집하여 Kafka로 전달합니다.

## 기술 스택

- **언어**: Python 3.11+
- **크롤링**: Scrapy
- **메시지 브로커**: Apache Kafka (`kafka-python`)
- **중복 제거**: 해시 기반 필터링

## 주요 기능

- 원티드, 사람인 등 채용 사이트 주기적 크롤링
- 수집된 공고를 Kafka `raw-job` 토픽으로 발행
- 제목·회사명·마감일 해싱을 통한 중복 공고 필터링

## 프로젝트 구조

```
catchjunior_crawling/
├── spiders/
│   ├── wanted_spider.py     # 원티드 크롤러
│   └── saramin_spider.py    # 사람인 크롤러
├── pipelines.py             # Kafka 발행 파이프라인
├── middlewares.py
├── items.py                 # 공고 데이터 모델
├── settings.py              # Scrapy 설정
└── requirements.txt
```

## 실행 방법

### 사전 조건
- Python 3.11+
- Kafka 실행 중

### 환경 설정

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 환경 변수

`.env` 파일을 생성합니다.

```env
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_RAW=raw-job
```

### 크롤러 실행

```bash
# 원티드 크롤링
scrapy crawl wanted

# 사람인 크롤링
scrapy crawl saramin
```

## Kafka 메시지 포맷

```json
{
  "title": "백엔드 개발자 (신입)",
  "company": "회사명",
  "url": "https://...",
  "description": "공고 원문...",
  "deadline": "2025-12-31",
  "source": "wanted",
  "collected_at": "2025-03-13T00:00:00"
}
```

## 중복 제거 로직

`title + company + deadline`을 SHA-256으로 해싱하여 이미 발행된 공고는 스킵합니다.
