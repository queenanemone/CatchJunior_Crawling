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

API_BASE = "https://oapi.saramin.co.kr/job-search"


class SaraminSpider(scrapy.Spider):
    """
    사람인 Open API 스파이더.
    access-key 발급 후 .env 에 SARAMIN_ACCESS_KEY=<your-key> 설정 필요.
    https://oapi.saramin.co.kr/guide/job-search
    """
    name = "saramin"
    allowed_domains = ["oapi.saramin.co.kr"]

    # 한 페이지당 최대 110건, 최대 10페이지 순회
    MAX_PAGES = 10
    COUNT = 110

    def start_requests(self):
        access_key = self.settings.get("SARAMIN_ACCESS_KEY", "")
        if not access_key:
            self.logger.error(
                "SARAMIN_ACCESS_KEY 가 설정되지 않았습니다. "
                ".env 파일에 SARAMIN_ACCESS_KEY=<your-key> 를 추가하세요."
            )
            return

        yield self._make_request(access_key, start=0)

    def parse(self, response):
        data = response.json()
        jobs_data = data.get("jobs", {})
        job_list = jobs_data.get("job", [])

        access_key = response.meta["access_key"]
        current_start = response.meta["start"]

        for job in job_list:
            item = JobPostItem()
            item["title"] = job.get("position", {}).get("title", "")
            item["company"] = job.get("company", {}).get("detail", {}).get("name", "")
            item["url"] = job.get("url", "")
            item["deadline"] = job.get("expiration-date", "")
            item["source"] = "saramin"
            item["description"] = self._build_description(job)
            item["tech_stacks"] = self._extract_tech_stacks(item["description"])
            item["collected_at"] = datetime.now().isoformat()
            yield item

        # 페이지네이션
        total = int(jobs_data.get("total", 0))
        next_start = current_start + self.COUNT
        if next_start < total and (current_start // self.COUNT) < self.MAX_PAGES - 1:
            yield self._make_request(access_key, start=next_start)

    def _make_request(self, access_key: str, start: int):
        params = (
            f"?access-key={access_key}"
            f"&job_type=1"          # 정규직
            f"&exp_min=0&exp_max=0" # 신입
            f"&fields=experience,job-code"
            f"&count={self.COUNT}"
            f"&start={start}"
            f"&sort=pd"             # 등록일 순
        )
        return scrapy.Request(
            url=f"{API_BASE}{params}",
            callback=self.parse,
            meta={"access_key": access_key, "start": start},
        )

    def _build_description(self, job: dict) -> str:
        parts = [
            job.get("position", {}).get("title", ""),
            job.get("position", {}).get("job-type", {}).get("string", ""),
            job.get("position", {}).get("experience-level", {}).get("string", ""),
            job.get("position", {}).get("required-education-level", {}).get("string", ""),
        ]
        return " ".join(filter(None, parts))

    def _extract_tech_stacks(self, text: str) -> list:
        text_lower = text.lower()
        return [kw for kw in TECH_KEYWORDS if kw.lower() in text_lower]
