import scrapy

class HealthMedicineSpider(scrapy.Spider):
    name = "health_medicine_spider"
    allowed_domains = ["adobochronicles.com"]
    start_urls = ["https://adobochronicles.com/category/health-medicine/"]
    max_pages = 200
    page_count = 0

    def parse(self, response):
        self.page_count += 1

        article_links = response.css('a[rel="bookmark"]::attr(href)').getall()
        for link in article_links:
            if "video" not in link:
                yield response.follow(link, callback=self.parse_article)

        if self.page_count < self.max_pages:
            next_page = response.css('a.next::attr(href)').get()
            if next_page and '/category/health-medicine/' in next_page:
                yield response.follow(next_page, callback=self.parse)

    def parse_article(self, response):
        title = response.css('h1.entry-title::text').get()

        # Extract all text inside <p> tags, including text in nested tags
        paragraphs = response.xpath('//article//p//text()').getall()

        # Skip if no non-empty <p> content is found
        if not paragraphs or not any(p.strip() for p in paragraphs):
            return

        full_text = ' '.join(p.strip() for p in paragraphs if p.strip())
        published_date = response.css('time.entry-date::attr(datetime)').get()

        # Extract category tags
        category_tags = response.css('span.cat-links a[rel="category tag"]::text').getall()
        category_tags = [tag.strip() for tag in category_tags if tag.strip()]
        category_string = ', '.join(category_tags)

        yield {
            "title": title.strip() if title else "",
            "url": response.url,
            "text": full_text,
            "published_date": published_date.strip() if published_date else "",
            "categories": category_string
        }
