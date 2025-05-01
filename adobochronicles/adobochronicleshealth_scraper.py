import scrapy

class HealthMedicineSpider(scrapy.Spider):
    name = "health_medicine_spider"
    allowed_domains = ["adobochronicles.com"]
    start_urls = ["https://adobochronicles.com/category/health-medicine/"]
    max_pages = 300
    page_count = 0

    def parse(self, response):
        self.page_count += 1
        article_links = response.css('a[rel="bookmark"]::attr(href)').getall()
        for link in article_links:
            if "video" not in link:
                yield response.follow(link, callback=self.parse_article)

        if self.page_count < self.max_pages:
            next_page = response.css('a.next::attr(href)').get()
            # Ensure it's still within the same category
            if next_page and '/category/health-medicine/' in next_page:
                yield response.follow(next_page, callback=self.parse)

    def parse_article(self, response):
        title = response.css('h1.entry-title::text').get()
        paragraphs = response.css('article p::text').getall()
        full_text = ' '.join(p.strip() for p in paragraphs if p.strip())
        published_date = response.css('time.entry-date::attr(datetime)').get()

        yield {
            "title": title.strip() if title else "",
            "url": response.url,
            "text": full_text,
            "published_date": published_date.strip() if published_date else ""
        }
