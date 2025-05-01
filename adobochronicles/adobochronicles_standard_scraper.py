import scrapy

class BookmarkSpider(scrapy.Spider):
    name = "bookmark_spider"
    allowed_domains = ["adobochronicles.com"]
    start_urls = ["https://adobochronicles.com/"]
    max_pages = 5
    page_count = 0

    def parse(self, response):
        self.page_count += 1
        article_links = response.css('a[rel="bookmark"]::attr(href)').getall()
        for link in article_links:
            yield response.follow(link, callback=self.parse_article)

        if self.page_count < self.max_pages:
            next_page = response.css('a.next::attr(href)').get()
            if next_page:
                yield response.follow(next_page, callback=self.parse)

    def parse_article(self, response):
        title = response.css('h1.entry-title::text').get()
        paragraphs = response.css('article p::text').getall()
        full_text = ' '.join(p.strip() for p in paragraphs if p.strip())
        yield {
            "title": title.strip() if title else "",
            "url": response.url,
            "text": full_text
        }
