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

BASE_URL = "https://jumpit.saramin.co.kr"
API_LIST = f"{BASE_URL}/api/positions?sort=rsp_rate&growthStage=신입&page=1"


class JumpitSpider(scrapy.Spider):
    """
    점핏 (IT 채용 특화 — 사람인 계열) 스파이더.
    JSON API 기반, 별도 인증 불필요.
    """
    name = "jumpit"
    allowed_domains = ["jumpit.saramin.co.kr"]

    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ko-KR,ko;q=0.9",
            "Referer": "https://jumpit.saramin.co.kr/",
            "Origin": "https://jumpit.saramin.co.kr",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        }
    }

    def start_requests(self):
        yield scrapy.Request(API_LIST, callback=self.parse, meta={"page": 1})

    def parse(self, response):
        data = response.json()
        result = data.get("result", {})
        positions = result.get("positions", [])

        for pos in positions:
            item = JobPostItem()
            item["title"] = pos.get("title", "")
            item["company"] = pos.get("companyName", "")
            item["url"] = f"{BASE_URL}/position/{pos.get('id')}"
            item["deadline"] = pos.get("closedAt", "")
            item["source"] = "jumpit"
            item["tech_stacks"] = self._extract_tech_stacks_from_tags(
                pos.get("techStacks", [])
            )
            item["collected_at"] = datetime.now().isoformat()
            item["description"] = ""

            yield scrapy.Request(
                url=f"{BASE_URL}/api/position/{pos.get('id')}",
                callback=self._parse_detail,
                cb_kwargs={"item": item},
            )

        # 페이지네이션
        total_pages = result.get("totalPages", 1)
        current_page = response.meta["page"]
        if current_page < total_pages:
            next_page = current_page + 1
            next_url = (
                f"{BASE_URL}/api/positions"
                f"?sort=rsp_rate&growthStage=신입&page={next_page}"
            )
            yield scrapy.Request(
                next_url,
                callback=self.parse,
                meta={"page": next_page},
            )

    def _parse_detail(self, response, item: JobPostItem):
        data = response.json().get("result", {})

        description_parts = [
            data.get("serviceIntro", ""),       # 서비스 소개
            data.get("responsibility", ""),     # 주요 업무
            data.get("qualification", ""),      # 자격 요건 ← 경력 분석 핵심
            data.get("preferredQualification", ""),  # 우대 사항
            data.get("benefit", ""),            # 복지
        ]
        item["description"] = "\n".join(filter(None, description_parts))

        # description 에서 추가 기술스택 추출
        existing = set(item.get("tech_stacks", []))
        from_desc = set(self._extract_tech_stacks_from_text(item["description"]))
        item["tech_stacks"] = list(existing | from_desc)

        yield item

    def _extract_tech_stacks_from_tags(self, tags: list) -> list:
        tag_names = " ".join(
            t if isinstance(t, str) else t.get("stackName", "") for t in tags
        )
        return self._extract_tech_stacks_from_text(tag_names)

    def _extract_tech_stacks_from_text(self, text: str) -> list:
        text_lower = text.lower()
        return [kw for kw in TECH_KEYWORDS if kw.lower() in text_lower]
