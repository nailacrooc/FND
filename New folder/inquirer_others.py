import scrapy
import re

class LatestStoriesSpider(scrapy.Spider):
    name = 'latest_stories_others'
    allowed_domains = [
        'inquirer.net', 'newsinfo.inquirer.net',
        'business.inquirer.net', 'technology.inquirer.net', 'sports.inquirer.net', 
        'lifestyle.inquirer.net', 'globalnation.inquirer.net'
    ]

    start_urls = [
        f'https://{domain}/category/latest-stories/page/{i}/'
        for domain in allowed_domains for i in range(1, 751)
    ]

    scraped_articles = 0
    max_articles = 2500

    seen_titles = set()
    seen_urls = set()

    health_keywords = [
        'health', 'hospital', 'doctor', 'vaccine', 'covid', 'pandemic',
        'medicine', 'nurse', 'disease', 'medical', 'virus', 'infection',
        'surgery', 'illness', 'mental', 'wellness', 'clinic', 'epidemic',
        'immunization', 'checkup', 'pediatric', 'cardiology', 'hmo',
        'philhealth', 'doh', 'healthcare', 'frontliner', 'fever', 'symptom',
        'quarantine', 'isolation', 'booster', 'telemedicine', 'malasakit',
        'sanitation', 'emergency room', 'resbakuna', 'health center'
    ]

    entertainment_keywords = [
        'celebrity', 'showbiz', 'movie', 'film', 'tv', 'series',
        'entertainment', 'actor', 'actress', 'drama', 'comedy',
        'concert', 'music', 'singer', 'band', 'theater', 'trailer',
        'award', 'premiere', 'netflix', 'hollywood', 'blockbuster',
        'teleserye', 'noontime show', 'gma', 'abs-cbn', 'kapamilya',
        'kapuso', 'viva', 'star cinema', 'oscars', 'grammys', 'p-pop',
        'k-pop', 'broadway', 'livestream', 'yt vlog', 'influencer'
    ]

    politics_keywords = [
        'election', 'politics', 'government', 'senate', 'congress',
        'president', 'candidate', 'vote', 'politician', 'policy',
        'debate', 'campaign', 'party', 'democracy', 'reform',
        'conservative', 'liberal', 'malacañang', 'bbm', 'duterte',
        'leni', 'robredo', 'comelec', 'barangay', 'mayor', 'governor',
        'vice president', 'house of representatives', 'supreme court',
        'protest', 'law', 'bill', 'charter change', 'oligarch',
        'red-tagging', 'dilg', 'dswd', 'state of the nation', 'senatorial'
    ]

    def parse(self, response):
        if self.scraped_articles >= self.max_articles:
            return

        articles = response.xpath('//h2/a')
        for article in articles:
            if self.scraped_articles >= self.max_articles:
                return

            title = article.xpath('text()').get()
            url = article.xpath('@href').get()

            if title and url:
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

        content_paragraphs = response.xpath(
            '//*[@id="FOR_target_content"]//p[not(@class="headertext") and not(@class="footertext") and not(starts-with(@id, "caption-attachment"))]//text()'
        ).getall()
        content = ' '.join(content_paragraphs)

        title_clean = self.clean_text(title)
        content_clean = self.clean_text(content)
        full_text = f"{title_clean} {content_clean}".lower()

        if self.is_filtered(full_text):
            return

        if title_clean in self.seen_titles or url in self.seen_urls:
            return

        if content_clean.strip():
            self.seen_titles.add(title_clean)
            self.seen_urls.add(url)

            self.scraped_articles += 1
            self.logger.info(f"[OTHERS] {self.scraped_articles}/{self.max_articles}: {title_clean}")
            yield {
                'title': title_clean,
                'content': content_clean,
                'url': url,
                'category': 'others'
            }

    def clean_text(self, text):
        if text:
            text = re.sub(r'[^\x00-\x7F]+', '', text)
            text = re.sub(r'\([^)]*\)', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
        return text

    def is_filtered(self, text):
        return any(keyword in text for keyword in (
            self.health_keywords + self.entertainment_keywords + self.politics_keywords
        ))
