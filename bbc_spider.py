import scrapy

class HealthSpider(scrapy.Spider):
    name = "health"
    allowed_domains = ["bbc.com"]
    start_urls = ["https://www.bbc.com/news/health"]

    def parse(self, response):
        # Find all article links on the health section page
        article_links = response.css('a.gs-c-promo-heading::attr(href)').getall()
        for link in article_links:
            if link.startswith("/news"):
                full_link = response.urljoin(link)
                yield scrapy.Request(full_link, callback=self.parse_article)

    def parse_article(self, response):
        title = response.css('h1::text').get()
        paragraphs = response.css('article p::text').getall()
        content = " ".join(paragraphs).strip()

        yield {
            'title': title,
            'content': content,
        }
