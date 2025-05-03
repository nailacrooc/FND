import scrapy

class BookmarkSpider(scrapy.Spider):
    name = "bookmark_spider"
    allowed_domains = ["adobochronicles.com"]
    start_urls = ["https://adobochronicles.com/category/politics/"]
    max_pages = 468
    page_count = 0

    def parse(self, response):
        self.page_count += 1
        article_links = response.css('a[rel="bookmark"]::attr(href)').getall()
        for link in article_links:
            if "video" not in link:  # Skip links containing 'video'
                yield response.follow(link, callback=self.parse_article)

        # Follow next page only within the politics category
        if self.page_count < self.max_pages:
            next_page = response.css('a.next::attr(href)').get()
            if next_page and '/category/politics/' in next_page:
                yield response.follow(next_page, callback=self.parse)

    def parse_article(self, response):
        title = response.css('h1.entry-title::text').get()

        # Extract all text from <p> tags including nested tags
        paragraphs = response.xpath('//article//p//text()').getall()

        # Skip if no <p> content
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
