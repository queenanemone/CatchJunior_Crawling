from datetime import datetime

import scrapy

from catchjunior.items import JobPostItem

TECH_KEYWORDS = [
    "Java", "Spring", "Python", "Django", "FastAPI",
    "JavaScript", "TypeScript", "React", "Next.js", "Vue",
    "Node.js", "Kotlin", "Swift", "Flutter", "Go",
    "Docker", "Kubernetes", "AWS", "MySQL", "PostgreSQL",
]


class WantedSpider(scrapy.Spider):
    name = "wanted"
    allowed_domains = ["www.wanted.co.kr"]

    # 신입(0년) 공고 API 예시 - 실제 엔드포인트 확인 후 수정
    start_urls = [
        "https://www.wanted.co.kr/api/v4/jobs?job_sort=job.latest_order&years=0&limit=100&offset=0"
    ]

    def parse(self, response):
        data = response.json()
        jobs = data.get("data", [])

        for job in jobs:
            item = JobPostItem()
            item["title"] = job.get("position")
            item["company"] = job.get("company", {}).get("name")
            item["url"] = f"https://www.wanted.co.kr/wd/{job.get('id')}"
            item["deadline"] = job.get("due_time", "")
            item["source"] = "wanted"
            item["tech_stacks"] = self._extract_tech_stacks(job.get("tags", []))
            item["collected_at"] = datetime.now().isoformat()
            item["description"] = ""  # 상세 페이지에서 수집

            yield response.follow(
                f"/api/v4/jobs/{job.get('id')}",
                callback=self._parse_detail,
                cb_kwargs={"item": item},
            )

        # 페이지네이션
        if jobs:
            offset = data.get("links", {}).get("next")
            if offset:
                yield response.follow(offset, callback=self.parse)

    def _parse_detail(self, response, item: JobPostItem):
        data = response.json().get("job", {})
        item["description"] = data.get("detail", {}).get("intro", "")
        yield item

    def _extract_tech_stacks(self, tags: list) -> list:
        tag_names = [t.get("title", "") for t in tags]
        return [kw for kw in TECH_KEYWORDS if kw.lower() in " ".join(tag_names).lower()]
