import scrapy


class JobPostItem(scrapy.Item):
    title = scrapy.Field()
    company = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()
    deadline = scrapy.Field()
    source = scrapy.Field()
    tech_stacks = scrapy.Field()
    collected_at = scrapy.Field()
