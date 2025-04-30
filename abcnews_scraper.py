import scrapy
from urllib.parse import urljoin

class ABCPoliticsSpider(scrapy.Spider):
    name = 'abc_politics'
    allowed_domains = ['abcnews.go.com']
    start_urls = ['https://abcnews.go.com/Politics']
    max_pages = 5  # Set your desired maximum number of pages here

    def __init__(self, *args, **kwargs):
        super(ABCPoliticsSpider, self).__init__(*args, **kwargs)
        self.page_count = 1

    def parse(self, response):
        # Extract all <a> tags with class 'AnchorLink'
        links = response.css('a.AnchorLink::attr(href)').getall()
        for link in links:
            full_url = urljoin(response.url, link)
            yield {'url': full_url}

        # Check if we've reached the maximum number of pages
        if self.page_count >= self.max_pages:
            return

        # Attempt to find the 'Next' page link
        next_page = response.css('a[aria-label="Next"]::attr(href)').get()
        if next_page:
            self.page_count += 1
            next_page_url = urljoin(response.url, next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse)
