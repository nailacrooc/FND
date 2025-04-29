import scrapy
import re

class LatestStoriesSpider(scrapy.Spider):
    name = 'latest_stories'
    allowed_domains = [
        'inquirer.net', 'newsinfo.inquirer.net',
        'business.inquirer.net', 'technology.inquirer.net', 'entertainment.inquirer.net'
    ]

    categories = {
        'entertainment': ('https://entertainment.inquirer.net/category/latest-stories/page/{}/', 2000),
        'health': [
            ('https://business.inquirer.net/category/latest-stories/science-technology-and-energy/science-and-health/page/{}/', 1000),
            ('https://technology.inquirer.net/category/latest-stories/health/page/{}/', 1000),
            ('https://globalnation.inquirer.net/category/world-news/asia-australia/page/{}/', 1000),
            ('https://globalnation.inquirer.net/category/world-news/us-canada/page/{}/', 1000),
            ('https://globalnation.inquirer.net/category/world-news/middle-east-africa/page/{}/', 1000),
            ('https://globalnation.inquirer.net/category/world-news/europe/page/{}/', 1000)
        ],
        'politics': [
            ('https://www.inquirer.net/category/philippine-elections/page/{}/', 1000),
            ('https://globalnation.inquirer.net/category/world-news/asia-australia/page/{}/', 1000),
            ('https://globalnation.inquirer.net/category/world-news/us-canada/page/{}/', 1000),
            ('https://globalnation.inquirer.net/category/world-news/middle-east-africa/page/{}/', 1000),
            ('https://globalnation.inquirer.net/category/world-news/europe/page/{}/', 1000)
        ]
    }

    scraped_articles = {
        'entertainment': 0,
        'health': 0,
        'politics': 0
    }
    max_articles = {
        'entertainment': 2000,
        'health': 2000,
        'politics': 2000
    }

    health_keywords = [
        'health', 'hospital', 'doctor', 'vaccine', 'covid',
        'pandemic', 'medicine', 'nurse', 'disease', 'medical',
        'virus', 'infection', 'surgery', 'illness', 'mental'
    ]

    def start_requests(self):
        for category, info in self.categories.items():
            if isinstance(info, list):
                for url_pattern, _ in info:
                    for i in range(1, 1001):
                        url = url_pattern.format(i)
                        yield scrapy.Request(url=url, callback=self.parse, meta={'category': category})
            else:
                url_pattern, _ = info
                for i in range(1, 1001):
                    url = url_pattern.format(i)
                    yield scrapy.Request(url=url, callback=self.parse, meta={'category': category})

    def parse(self, response):
        category = response.meta.get('category')

        if self.scraped_articles[category] >= self.max_articles[category]:
            return

        articles = response.xpath('//h2/a')

        for article in articles:
            title = article.xpath('text()').get()
            url = article.xpath('@href').get()

            if url and title:
                # Only collect relevant health articles
                if category == 'health' and not self.is_health_related(title):
                    continue
                # Avoid health-related duplication under politics
                if category == 'politics' and self.is_health_related(title):
                    continue

                full_url = response.urljoin(url)

                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse_article,
                    meta={
                        'title': title,
                        'url': full_url,
                        'category': category
                    }
                )

    def parse_article(self, response):
        category = response.meta.get('category')

        if self.scraped_articles[category] >= self.max_articles[category]:
            return

        title = response.meta.get('title')
        url = response.meta.get('url')

        content_paragraphs = response.xpath('//*[@id="FOR_target_content"]//p[not(starts-with(@id, "caption-attachment"))]//text()').getall()
        content = ' '.join(content_paragraphs)

        title = self.clean_text(title)
        content = self.clean_text(content)

        if content.strip():
            self.scraped_articles[category] += 1
            self.logger.info(f"[{category.upper()}] {self.scraped_articles[category]}/{self.max_articles[category]}: {title}")
            yield {
                'title': title,
                'content': content,
                'url': url,
                'category': category
            }

    def clean_text(self, text):
        if text:
            text = re.sub(r'[^\x00-\x7F]+', '', text)
            text = re.sub(r'\([^)]*\)', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
        return text

    def is_health_related(self, title):
        title_lower = title.lower()
        return any(keyword in title_lower for keyword in self.health_keywords)

# scrapy crawl latest_stories -o latest_stories.csv