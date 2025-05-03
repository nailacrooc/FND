import scrapy
import re


class ApNewsEntertainmentSpider(scrapy.Spider):
    name = "ap_news_entertainment"
    start_urls = ['https://apnews.com/entertainment?p=1']
    article_count = 0
    max_articles = 2000  # Set your limit between 1000–2000

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'ap_entertainment_articles.csv',
        'FEED_EXPORT_FIELDS': ['title', 'content', 'url', 'category'],
        'FEED_OVERWRITE': True,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 1,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'AUTOTHROTTLE_DEBUG': False,
    }

    def parse(self, response):
        if self.article_count >= self.max_articles:
            return

        article_links = response.css('h3.PagePromo-title a::attr(href)').getall()
        for article in article_links:
            full_url = response.urljoin(article)
            yield scrapy.Request(url=full_url, callback=self.parse_article)

        # Pagination
        current_page = int(response.url.split('=')[-1])
        next_page = f'https://apnews.com/entertainment?p={current_page + 1}'
        yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_article(self, response):
        title = response.css('h1.Page-headline::text').get()
        paragraphs = []

        for p in response.css('div.RichTextStoryBody.RichTextBody p'):
            if p.xpath('ancestor::div[contains(@class, "Infobox")]'):
                continue
            full_text = ''.join(p.xpath('.//text()').getall())
            paragraphs.append(full_text)

        if title and paragraphs:
            raw_text = ' '.join(paragraphs)
            cleaned_title = self.clean_text(title)
            cleaned_content = self.clean_text(raw_text)

            self.article_count += 1

            yield {
                'title': cleaned_title,
                'content': cleaned_content,
                'url': response.url,
                'category': 'entertainment'
            }

    def clean_text(self, text):
        return re.sub(r'[^\x00-\x7F]+', '', text).strip()
