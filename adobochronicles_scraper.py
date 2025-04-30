import scrapy

class AdoboChroniclesSpider(scrapy.Spider):
    name = "adobo_chronicles"
    start_urls = ['https://adobochronicles.com/']

    def parse(self, response):
        # Extract article titles under h1 with class 'entry-title'
        for article in response.css('h1.entry-title'):
            title = article.css('::text').get()
            yield {'title': title}

        # Follow pagination link (Older posts button)
        next_page = response.css('span.custom-cursor-on-hover button::text').get()
        if next_page and "Older posts" in next_page:
            next_page_link = response.xpath("//span[contains(@class, 'custom-cursor-on-hover')]/button/ancestor::a/@href").get()
            if next_page_link:
                yield response.follow(next_page_link, self.parse)

# Scrapy settings for exporting data to CSV
FEEDS = {
    'articles.csv': {
        'format': 'csv',
        'overwrite': True
    },
}
