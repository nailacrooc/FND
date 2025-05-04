import scrapy
import re


class PoliticsLinksSpider(scrapy.Spider):
    name = "politics_links"
    allowed_domains = ["thepoke.com"]
    start_urls = ['https://www.thepoke.com/category/politics/']

    # Set this to control max pages (e.g., 5 pages)
    max_pages = 99

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page_count = 1

    def parse(self, response):
        # Extract <a> tags inside <article class="boxgrid">
        articles = response.css('article.boxgrid')
        for article in articles:
            for a_tag in article.css('a'):
                href = a_tag.attrib.get('href', '')
                if href:
                    yield response.follow(href, self.parse_article)

        # Follow pagination if under limit
        if self.page_count < self.max_pages:
            next_page = response.css('div.prev a::attr(href)').get()
            if next_page and re.match(r'https://www\.thepoke\.com/category/politics/page/\d+/?', next_page):
                self.page_count += 1
                yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        # Extract headline (assumes <h1> is used)
        headline = response.css('h1::text').get()
        headline = headline.strip() if headline else ''

        # Extract only <p> tags under <div class="entry normal js-article-body">
        p_tags = response.css('div.entry.normal.js-article-body > p::text').getall()
        p_tags = [p.strip() for p in p_tags if p.strip()]

        if p_tags:
            p_tags = p_tags[:-1]  # Optional: remove last paragraph

        yield {
            'headline': headline,
            'url': response.url,
            'content': ' '.join(p_tags)
        }
