from datetime import datetime

import scrapy

from catchjunior.items import JobPostItem

TECH_KEYWORDS = [
    "Java", "Spring", "Spring Boot", "Python", "Django", "FastAPI",
    "JavaScript", "TypeScript", "React", "Next.js", "Vue", "Angular",
    "Node.js", "Kotlin", "Swift", "Flutter", "Go", "Rust", "C++", "C#",
    "Docker", "Kubernetes", "AWS", "GCP", "Azure",
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
    "Kafka", "RabbitMQ", "gRPC", "GraphQL",
    "Git", "Linux", "Terraform", "Jenkins", "CI/CD",
]

BASE_URL = "https://www.wanted.co.kr"
API_LIST = (
    f"{BASE_URL}/api/v4/jobs"
    "?job_sort=job.latest_order"
    "&years=0"          # 신입(0년)
    "&limit=100"
    "&offset=0"
)


class WantedSpider(scrapy.Spider):
    name = "wanted"
    allowed_domains = ["www.wanted.co.kr"]

    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ko-KR,ko;q=0.9",
            "Referer": "https://www.wanted.co.kr/",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        }
    }

    def start_requests(self):
        yield scrapy.Request(API_LIST, callback=self.parse)

    def parse(self, response):
        data = response.json()
        jobs = data.get("data", [])

        for job in jobs:
            item = JobPostItem()
            item["title"] = job.get("position", "")
            item["company"] = job.get("company", {}).get("name", "")
            item["url"] = f"{BASE_URL}/wd/{job.get('id')}"
            item["deadline"] = job.get("due_time", "")
            item["source"] = "wanted"
            item["tech_stacks"] = self._extract_tech_stacks_from_tags(job.get("tags", []))
            item["collected_at"] = datetime.now().isoformat()
            item["description"] = ""

            yield scrapy.Request(
                url=f"{BASE_URL}/api/v4/jobs/{job.get('id')}",
                callback=self._parse_detail,
                cb_kwargs={"item": item},
            )

        # 페이지네이션 — links.next 가 상대경로로 오는 경우 처리
        next_url = data.get("links", {}).get("next")
        if next_url and jobs:
            if next_url.startswith("http"):
                yield scrapy.Request(next_url, callback=self.parse)
            else:
                yield scrapy.Request(f"{BASE_URL}{next_url}", callback=self.parse)

    def _parse_detail(self, response, item: JobPostItem):
        job = response.json().get("job", {})
        detail = job.get("detail", {})

        # 경력 판별에 핵심적인 필드들을 합쳐서 description으로 저장
        description_parts = [
            detail.get("intro", ""),           # 회사 소개
            detail.get("main_tasks", ""),      # 주요 업무
            detail.get("requirements", ""),    # 자격 요건 ← 경력 분석 핵심
            detail.get("preferred_points", ""), # 우대 사항
            detail.get("benefits", ""),        # 복지
        ]
        item["description"] = "\n".join(filter(None, description_parts))

        # 태그에 없던 기술스택을 description에서 추가 추출
        existing = set(item.get("tech_stacks", []))
        from_desc = set(self._extract_tech_stacks_from_text(item["description"]))
        item["tech_stacks"] = list(existing | from_desc)

        yield item

    def _extract_tech_stacks_from_tags(self, tags: list) -> list:
        tag_names = " ".join(t.get("title", "") for t in tags)
        return self._extract_tech_stacks_from_text(tag_names)

    def _extract_tech_stacks_from_text(self, text: str) -> list:
        text_lower = text.lower()
        return [kw for kw in TECH_KEYWORDS if kw.lower() in text_lower]
