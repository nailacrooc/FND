import scrapy
import re

class LatestStoriesSpider(scrapy.Spider):
    name = 'latest_stories_others'
    allowed_domains = [
        'inquirer.net', 'newsinfo.inquirer.net',
        'business.inquirer.net', 'technology.inquirer.net', 'entertainment.inquirer.net'
    ]

    # Only the "others" category
    categories = {
        'others': ('https://newsinfo.inquirer.net/category/latest-stories/page/{}/', 1000)
    }

    scraped_articles = {
        'others': 0
    }

    max_articles = {
        'others': 1000
    }

    # Health, Entertainment, and Politics keywords
    health_keywords = [
        'health', 'hospital', 'doctor', 'vaccine', 'covid',
        'pandemic', 'medicine', 'nurse', 'disease', 'medical',
        'virus', 'infection', 'surgery', 'illness', 'mental'
    ]

    entertainment_keywords = [
        'celebrity', 'showbiz', 'movie', 'film', 'tv', 'series',
        'entertainment', 'actor', 'actress', 'drama', 'comedy',
        'concert', 'music', 'singer', 'band', 'theater', 'trailer',
        'award', 'premiere', 'netflix'
    ]

    politics_keywords = [
        'election', 'politics', 'government', 'senate', 'congress',
        'president', 'candidate', 'vote', 'politician', 'policy',
        'debate', 'campaign', 'party', 'democracy', 'reform', 'conservative', 'liberal'
    ]

    def start_requests(self):
        for category, info in self.categories.items():
            url_pattern, _ = info
            for i in range(1, 1001):  # 20 pages to keep total near 1000
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
                # Exclude health, entertainment, and politics articles from the "others" category
                if self.is_health_related(title) or self.is_entertainment_related(title) or self.is_politics_related(title):
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

        content_paragraphs = response.xpath(
            '//*[@id="FOR_target_content"]//p[not(@class="headertext") and not(@class="footertext") and not(starts-with(@id, "caption-attachment"))]//text()'
        ).getall()
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

    def is_entertainment_related(self, title):
        title_lower = title.lower()
        return any(keyword in title_lower for keyword in self.entertainment_keywords)

    def is_politics_related(self, title):
        title_lower = title.lower()
        return any(keyword in title_lower for keyword in self.politics_keywords)
