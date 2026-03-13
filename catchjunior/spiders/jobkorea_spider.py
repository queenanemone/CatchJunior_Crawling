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

BASE_URL = "https://www.jobkorea.co.kr"
# 신입 개발자 공고 검색 (careerType=1: 신입, cat=it: IT 직군)
START_URL = (
    f"{BASE_URL}/Search/"
    "?stext=개발자"
    "&careerType=1"
    "&tabType=recruit"
    "&Page_No=1"
)


class JobkoreaSpider(scrapy.Spider):
    """
    잡코리아 HTML 파싱 스파이더.
    신입 개발자 공고를 수집합니다.
    HTML 구조 변경 시 CSS 셀렉터 업데이트 필요.
    """
    name = "jobkorea"
    allowed_domains = ["www.jobkorea.co.kr"]

    custom_settings = {
        "DOWNLOAD_DELAY": 2.0,       # 잡코리아 서버 부하 방지
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,*/*",
            "Accept-Language": "ko-KR,ko;q=0.9",
            "Referer": "https://www.jobkorea.co.kr/",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        },
    }

    def start_requests(self):
        yield scrapy.Request(START_URL, callback=self.parse, meta={"page": 1})

    def parse(self, response):
        # 공고 목록에서 상세 링크 추출
        job_links = response.css("a.title::attr(href)").getall()

        # 목록 페이지에서 링크를 못 찾으면 대체 셀렉터 시도
        if not job_links:
            job_links = response.css(
                ".list-recruit-content .recruit-info a::attr(href)"
            ).getall()

        for link in job_links:
            if not link.startswith("http"):
                link = f"{BASE_URL}{link}"
            yield scrapy.Request(link, callback=self._parse_detail)

        # 페이지네이션 (최대 5페이지)
        current_page = response.meta["page"]
        if current_page < 5:
            next_page = current_page + 1
            next_url = START_URL.replace(
                f"Page_No={current_page}", f"Page_No={next_page}"
            )
            yield scrapy.Request(
                next_url,
                callback=self.parse,
                meta={"page": next_page},
            )

    def _parse_detail(self, response):
        item = JobPostItem()

        # 제목
        item["title"] = (
            response.css("h1.title::text").get("")
            or response.css(".recruit-title::text").get("")
        ).strip()

        # 회사명
        item["company"] = (
            response.css("a.coName::text").get("")
            or response.css(".corp-name-link::text").get("")
        ).strip()

        item["url"] = response.url
        item["source"] = "jobkorea"

        # 마감일
        deadline_text = response.css(".info-period span::text").get("")
        item["deadline"] = deadline_text.strip()

        # 상세 내용 (자격요건, 우대사항 포함)
        description_parts = response.css(
            ".tbCol.tbCoContents *::text, "
            ".job-section *::text, "
            ".cont-detail *::text"
        ).getall()
        item["description"] = " ".join(
            t.strip() for t in description_parts if t.strip()
        )

        item["tech_stacks"] = self._extract_tech_stacks(item["description"])
        item["collected_at"] = datetime.now().isoformat()

        if item["title"] and item["company"]:
            yield item
        else:
            self.logger.warning("파싱 실패 (제목/회사명 없음): %s", response.url)

    def _extract_tech_stacks(self, text: str) -> list:
        text_lower = text.lower()
        return [kw for kw in TECH_KEYWORDS if kw.lower() in text_lower]
