import scrapy
import re

class PbsPoliticsSpider(scrapy.Spider):
    name = "pbs_politics"
    allowed_domains = ["pbs.org"]
    start_urls = ["https://www.pbs.org/newshour/politics"]
    article_count = 0
    max_articles = 1500

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'pbs_politics_articles.csv',
        'FEED_EXPORT_FIELDS': ['title', 'content', 'url', 'category'],
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_MAX_DELAY': 1,
        'DOWNLOAD_DELAY': 0.1,
        'ROBOTSTXT_OBEY': True,
    }

    def parse(self, response):
        if self.article_count >= self.max_articles:
            return

        keywords = ['politics', 'biden', 'trump', 'congress', 'senate', 'house', 'republican', 'democrat',
                    'supreme court', 'election', 'vote', 'legislation', 'campaign', 'policy', 'white house']

        articles = response.css('div.archive-list a.card-horiz__title')

        for link in articles:
            url = link.css('::attr(href)').get()
            text = link.css('::text').get() or ''
            full_url = response.urljoin(url)

            if any(keyword in url.lower() or keyword in text.lower() for keyword in keywords):
                if self.article_count >= self.max_articles:
                    break
                yield scrapy.Request(full_url, callback=self.parse_article)

        next_page = response.css('a.pagination__link__next::attr(href)').get()
        if next_page and self.article_count < self.max_articles:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def parse_article(self, response):
        title = response.css('h1.video-single__title::text').get() or \
                response.css('h1.post__title::text').get()
        
        paragraphs = response.css('div.vt__excerpt.body-text p::text').getall()

        if not paragraphs:
            paragraphs = response.css('div.body-text p:not(.invite_body)')

            # Get text, excluding any <a> inside <p>
            cleaned_paragraphs = []
            for p in paragraphs:
                text = ''.join(p.css('::text').getall())
                cleaned_paragraphs.append(text)
            paragraphs = cleaned_paragraphs

        if title and paragraphs:
            self.article_count += 1
            raw_content = ' '.join(paragraphs)
            cleaned_title = self.clean_text(title)
            cleaned_content = self.clean_text(raw_content)

            yield {
                'title': cleaned_title,
                'content': cleaned_content,
                'url': response.url,
                'category': 'politics'
            }

    def clean_text(self, text):
        # Keep ASCII characters only
        return re.sub(r'[^\x00-\x7F]+', ' ', text).strip()
