import scrapy

class NewsSpider(scrapy.Spider):
    name = "news"
    start_urls = ['https://news10live.com/']

    def parse(self, response):
        # Extract article links with the class 'read-more'
        for article in response.css('article'):
            read_more_link = article.css('.read-more::attr(href)').get()
            if read_more_link:
                yield response.follow(read_more_link, self.parse_article)

        # Follow pagination links if available
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        # Extract paragraphs from the article
        paragraphs = response.css('p::text').getall()
        content = ' '.join(paragraph.strip() for paragraph in paragraphs)
        yield {
            'url': response.url,
            'content': content
        }

# Scrapy settings for exporting data to CSV
FEEDS = {
    'articles.csv': {
        'format': 'csv',
        'overwrite': True
    },
}