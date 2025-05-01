import scrapy
import re


class GuardianScraper(scrapy.Spider):
    name = "guardian_scraper"
    allowed_domains = ['theguardian.com']

    section_urls = {
        'health': [
            'https://www.theguardian.com/society/health',
            'https://www.theguardian.com/society/mental-health',
            'https://www.theguardian.com/science/medical-research',
            'https://www.theguardian.com/lifeandstyle/health-and-wellbeing',
            'https://www.theguardian.com/us-news/healthcare',
        ],
        'politics': [
            'https://www.theguardian.com/politics/all',
            'https://www.theguardian.com/politics/localgovernment',
            'https://www.theguardian.com/politics/local-elections',
            'https://www.theguardian.com/politics/foreignpolicy',
        ],
        'entertainment': [
            'https://www.theguardian.com/lifeandstyle/celebrity',
            'https://www.theguardian.com/music/popandrock',
            'https://www.theguardian.com/culture/television',
            'https://www.theguardian.com/tv-and-radio/us-television',
            'https://www.theguardian.com/film/all',
        ]
    }

    max_articles_per_category = 1000
    max_pages = 50
    articles_scraped = {'health': 0, 'politics': 0, 'entertainment': 0}
    seen_urls = set()

    health_keywords = [
        'health', 'medicine', 'wellness', 'disease', 'treatment', 'vaccine', 'healthcare',
        'mental health', 'fitness', 'nutrition', 'prevention', 'surgery', 'hospital', 'doctor',
        'illness', 'therapy', 'cure', 'health crisis', 'epidemic', 'pandemic', 'wellbeing',
        'exercise', 'mental illness', 'mental', 'doctors', 'patients', 'health advice', 'care'
    ]

    politics_keywords = [
        'election', 'government', 'policy', 'politics', 'political', 'senate', 'parliament',
        'prime minister', 'president', 'lawmaker', 'congress', 'bill', 'vote', 'voting',
        'campaign', 'diplomacy', 'legislation', 'republican', 'democrat', 'party', 'minister',
        'local government', 'foreign policy', 'MP', 'governance', 'administration', 'cabinet'
    ]

    entertainment_keywords = [
        'celebrity', 'music', 'film', 'movie', 'tv', 'television', 'series', 'actor', 'actress',
        'director', 'award', 'concert', 'drama', 'comedy', 'blockbuster', 'hollywood',
        'soundtrack', 'showbiz', 'red carpet', 'entertainment', 'box office', 'screen', 'screenplay'
    ]

    keyword_map = {
        'health': health_keywords,
        'politics': politics_keywords,
        'entertainment': entertainment_keywords,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.compiled_keywords = {
            cat: re.compile(r'\b(?:' + '|'.join(map(re.escape, kws)) + r')\b', re.IGNORECASE)
            for cat, kws in self.keyword_map.items()
        }

    custom_settings = {
        'CONCURRENT_REQUESTS': 16,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
        'DOWNLOAD_DELAY': 0.25,
        'RETRY_ENABLED': False,
        'DOWNLOAD_TIMEOUT': 10,
        'LOG_LEVEL': 'INFO',
        'ROBOTSTXT_OBEY': True
    }

    def start_requests(self):
        for category, urls in self.section_urls.items():
            for base_url in urls:
                for page in range(1, self.max_pages + 1):
                    if self.articles_scraped[category] >= self.max_articles_per_category:
                        break
                    paginated_url = f"{base_url}?page={page}"
                    yield scrapy.Request(
                        url=paginated_url,
                        callback=self.parse_listing,
                        meta={'category': category}
                    )

    def parse_listing(self, response):
        category = response.meta['category']
        if self.articles_scraped[category] >= self.max_articles_per_category:
            return

        article_links = response.xpath('//*[@id="maincontent"]//a[@aria-label]/@href').getall()
        article_links = list(set(article_links))  # Deduplicate

        for link in article_links:
            full_url = response.urljoin(link)
            if full_url not in self.seen_urls:
                self.seen_urls.add(full_url)
                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse_article,
                    meta={'category': category}
                )

    def parse_article(self, response):
        category = response.meta['category']
        if self.articles_scraped[category] >= self.max_articles_per_category:
            return

        title_parts = response.xpath('//h1//text()').getall()
        title = ' '.join([t.strip() for t in title_parts if t.strip()])
        title = self.clean_text(title) if title else 'N/A'

        paragraphs = response.xpath('//main//p//text()').getall()
        content = ' '.join([self.clean_text(p) for p in paragraphs if p.strip()])
        if not content:
            return

        full_text = f"{title.lower()} {content.lower()}"

        matched_categories = [
            cat for cat, pattern in self.compiled_keywords.items()
            if pattern.search(full_text)
        ]

        if len(matched_categories) != 1:
            return  # Skip if matched multiple or no categories

        matched_category = matched_categories[0]
        if matched_category != category:
            return  # Mismatch: skip

        self.articles_scraped[category] += 1
        yield {
            'title': title,
            'content': content,
            'url': response.url,
            'category': category
        }

    def clean_text(self, text):
        text = re.sub(r'\([^)]*\)', '', text)
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
