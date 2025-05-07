import scrapy
import re
#import csv
#import os

class NewsMedicalSpider(scrapy.Spider):
    name = "news_medical"
    start_urls = ["https://www.news-medical.net/medical/articles"]
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'articles.csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'DOWNLOAD_DELAY': 0.5
    }

    article_count = 0
    max_articles = 2000

    def parse(self, response):
        # Select all article <a> links from main list
        links = response.xpath('//div[@class="posts publishables-list-wrap first-item-larger"]//a/@href').extract()
        
        for href in links:
            if self.article_count >= self.max_articles:
                break
            if "page=" in href:  # Skip pagination links inside the article block
                continue
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_article, meta={'url': url})

        # Pagination: look for the Next link
        next_page_relative = response.xpath('//*[@id="main"]/div[3]/div[41]//a[text()="Next"]/@href').get()
        if next_page_relative and self.article_count < self.max_articles:
            next_page_url = response.urljoin(next_page_relative)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_article(self, response):
        title = response.xpath('//*[@id="main"]/div[4]/div[1]/h1/text()').get()
        paragraphs = response.xpath('//*[@id="ctl00_cphBody_divText"]/p')

        clean_paragraphs = []
        for p in paragraphs:
            # Skip <p> tags that contain links
            if p.xpath('.//a'):
                continue
            text = p.xpath('string(.)').get()
            if text:
                ascii_text = re.sub(r'[^\x00-\x7F]+', ' ', text)
                clean_paragraphs.append(ascii_text.strip())

        content = ' '.join(clean_paragraphs).strip()

        if title and content:
            self.article_count += 1
            yield {
                'title': re.sub(r'[^\x00-\x7F]+', ' ', title.strip()),
                'content': content,
                'URL': response.meta['url'],
                'category': 'health'
            }
