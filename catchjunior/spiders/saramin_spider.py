from datetime import datetime

import scrapy

from catchjunior.items import JobPostItem

TECH_KEYWORDS = [
    "Java", "Spring", "Python", "Django", "FastAPI",
    "JavaScript", "TypeScript", "React", "Next.js", "Vue",
    "Node.js", "Kotlin", "Swift", "Flutter", "Go",
    "Docker", "Kubernetes", "AWS", "MySQL", "PostgreSQL",
]


class SaraminSpider(scrapy.Spider):
    name = "saramin"
    allowed_domains = ["www.saramin.co.kr"]

    # 신입(경력 0년) 공고 검색 - 실제 파라미터 확인 후 수정
    start_urls = [
        "https://www.saramin.co.kr/zf_user/jobs/list/job-category?cat_kewd=84&exp_cd=1&page=1"
    ]

    def parse(self, response):
        job_links = response.css("a.job_tit::attr(href)").getall()

        for link in job_links:
            yield response.follow(link, callback=self._parse_detail)

        # 페이지네이션
        next_page = response.css("a.btn_next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def _parse_detail(self, response):
        item = JobPostItem()
        item["title"] = response.css("h1.tit_job::text").get("").strip()
        item["company"] = response.css("a.company::text").get("").strip()
        item["url"] = response.url
        item["description"] = " ".join(response.css("div.job_detail *::text").getall())
        item["deadline"] = response.css("span.date::text").get("").strip()
        item["source"] = "saramin"
        item["tech_stacks"] = self._extract_tech_stacks(item["description"])
        item["collected_at"] = datetime.now().isoformat()
        yield item

    def _extract_tech_stacks(self, description: str) -> list:
        return [kw for kw in TECH_KEYWORDS if kw.lower() in description.lower()]
