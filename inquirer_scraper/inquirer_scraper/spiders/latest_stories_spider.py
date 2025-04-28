import scrapy
import re

class LatestStoriesSpider(scrapy.Spider):
    name = 'latest_stories'
    allowed_domains = ['newsinfo.inquirer.net']
    start_urls = [f'https://newsinfo.inquirer.net/category/latest-stories/page/{i}' for i in range(1, 301)]  # Crawl pages 1–200
    scraped_articles = 0
    max_articles = 1000

    def parse(self, response):
        if self.scraped_articles >= self.max_articles:
            return

        articles = response.xpath('//*[@id="inq-channel-left"]//h2/a')

        for article in articles:
            title = article.xpath('text()').get()
            url = article.xpath('@href').get()

            if url and title:
                full_url = response.urljoin(url)

                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse_article,
                    meta={'title': title, 'url': full_url}
                )

    def parse_article(self, response):
        if self.scraped_articles >= self.max_articles:
            return

        title = response.meta.get('title')
        url = response.meta.get('url')

        # ✅ Extract <p> inside FOR_target_content that do NOT have IDs starting with "caption-attachment"
        content_paragraphs = response.xpath('//*[@id="FOR_target_content"]//p[not(starts-with(@id, "caption-attachment"))]//text()').getall()

        content = ' '.join(content_paragraphs)

        # Clean text
        title = self.clean_text(title)
        content = self.clean_text(content)

        if content.strip():
            self.scraped_articles += 1
            self.logger.info(f"Scraped article {self.scraped_articles}/{self.max_articles}: {title}")
            yield {
                'title': title,
                'content': content,
                'url': url
            }

    def clean_text(self, text):
        if text:
            text = re.sub(r'[^\x00-\x7F]+', '', text)        # Remove non-ASCII characters
            text = re.sub(r'\([^)]*\)', '', text)            # Remove text inside parentheses (and parentheses)
            text = re.sub(r'\s+', ' ', text).strip()         # Normalize whitespace
        return text

# This spider can be run using the command:
# scrapy crawl latest_stories -o latest_stories.csv