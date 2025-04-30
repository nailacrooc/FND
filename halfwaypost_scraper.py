import scrapy

class HalfwayPostSpider(scrapy.Spider):
    name = 'halfway'
    allowed_domains = ['halfwaypost.com']
    max_pages = 111  # <-- EDIT THIS VALUE AS NEEDED

    def start_requests(self):
        for i in range(1, self.max_pages + 1):
            url = f'https://halfwaypost.com/page/{i}/'
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        article_links = response.css('a[rel="bookmark"]::attr(href)').getall()
        for link in article_links:
            yield response.follow(link, callback=self.parse_article)

    def parse_article(self, response):
        # Skip if the article contains <ul> or <ol> with class wp-block-list
        if response.css('ul.wp-block-list, ol.wp-block-list'):
            self.logger.info(f"Skipped article with list block: {response.url}")
            return

        title = response.css('h1.entry-title::text').get()
        paragraphs = response.css('div.entry-content p::text').getall()
        content = "\n".join(paragraphs).strip()

        yield {
            'url': response.url,
            'title': title,
            'content': content
        }
