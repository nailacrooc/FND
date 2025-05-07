import scrapy
import re


class ApNewsSpider(scrapy.Spider):
    name = "ap_news_politics"
    start_urls = ['https://apnews.com/politics?p=1']  # Start at page 1
    article_count = 0  # Variable to track the number of articles scraped
    max_articles = 2000  # Set maximum articles to scrape (between 1000-2000)

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'ap_politics_articles.csv',
        'FEED_EXPORT_FIELDS': ['title', 'content', 'url', 'category'],
        'FEED_OVERWRITE': True,  # This ensures the CSV is overwritten each time
        'AUTOTHROTTLE_ENABLED': True,  # Enable autothrottle
        'AUTOTHROTTLE_START_DELAY': 1,  # Initial download delay in seconds
        'AUTOTHROTTLE_MAX_DELAY': 1,  # Set max download delay to 1 second
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,  # Target concurrency per server
        'AUTOTHROTTLE_DEBUG': False,  # Disable debug info (set True for more detailed info)
    }

    def parse(self, response):
        # If we reach the maximum number of articles, stop the crawl
        if self.article_count >= self.max_articles:
            return
        
        # Extract article links
        article_links = response.css('h3.PagePromo-title a::attr(href)').getall()
        for article in article_links:
            full_url = response.urljoin(article)
            yield scrapy.Request(url=full_url, callback=self.parse_article)

        # Handle pagination (look for the next page link)
        next_page = response.url.split('?p=')[0] + '?p=' + str(int(response.url.split('=')[1]) + 1)  # Increment the page number
        yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_article(self, response):
        title = response.css('h1.Page-headline::text').get()
        paragraphs = []

        for p in response.css('div.RichTextStoryBody.RichTextBody p'):
            # Skip <p> inside div.Infobox
            if p.xpath('ancestor::div[contains(@class, "Infobox")]'):
                continue

            full_text = ''.join(p.xpath('.//text()').getall())  # include text inside <a> and others
            paragraphs.append(full_text)

        if title and paragraphs:
            raw_text = ' '.join(paragraphs)
            cleaned_title = self.clean_text(title)
            cleaned_content = self.clean_text(raw_text)

            # Increment article count after scraping an article
            self.article_count += 1

            yield {
                'title': cleaned_title,
                'content': cleaned_content,
                'url': response.url,
                'category': 'politics'
            }

    def clean_text(self, text):
        # Remove any non-ASCII characters (including unusual/unwanted symbols)
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        return text.strip()
