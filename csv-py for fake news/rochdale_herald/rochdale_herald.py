import scrapy
from scrapy.exceptions import CloseSpider
import re

class Scraper(scrapy.Spider):
    name = "rochdale_herald"
    base_url = "https://rochdaleherald.co.uk/other/sport/"
    start_page = 1
    max_pages = 1  # Adjust this to crawl more pages

    def start_requests(self):
        for page_num in range(self.start_page, self.max_pages + 1):
            page_url = f"{self.base_url}/page/{page_num}/"
            print(f"Scraping page: {page_url}")
            yield scrapy.Request(url=page_url, callback=self.parse_page)

    def parse_page(self, response):
        # Scrape from div.td-ss-main-content
        article_links = response.xpath('//div[contains(@class, "td-ss-main-content")]//a[@href and @title]')
        
        for article in article_links:
            title = article.xpath('./@title').get()
            link = article.xpath('./@href').get()

            if not (title and link):
                continue

            full_url = response.urljoin(link)

            # Extract year from URL using regex
            match = re.search(r'/(\d{4})/\d{2}/\d{2}/', full_url)
            if match:
                year = int(match.group(1))
                if year < 2020:
                    self.logger.info(f"Skipping article from {year}: {full_url}")
                    continue
            else:
                self.logger.warning(f"No date in URL: {full_url}")
                continue  # Optionally skip if no date found

            yield scrapy.Request(
                url=full_url,
                callback=self.parse_article,
                meta={"title": title.strip(), "link": full_url, "year": year}
            )
        
        # Scrape from div.td-pb-span12
        article_links_2 = response.xpath('//div[contains(@class, "td-pb-span12")]//a[@href and @title]')
        
        for article in article_links_2:
            title = article.xpath('./@title').get()
            link = article.xpath('./@href').get()

            if not (title and link):
                continue

            full_url = response.urljoin(link)

            # Extract year from URL using regex
            match = re.search(r'/(\d{4})/\d{2}/\d{2}/', full_url)
            if match:
                year = int(match.group(1))
                if year < 2020:
                    self.logger.info(f"Skipping article from {year}: {full_url}")
                    continue
            else:
                self.logger.warning(f"No date in URL: {full_url}")
                continue  # Optionally skip if no date found

            yield scrapy.Request(
                url=full_url,
                callback=self.parse_article,
                meta={"title": title.strip(), "link": full_url, "year": year}
            )

    def parse_article(self, response):
        title = response.meta["title"]
        link = response.meta["link"]
        year = response.meta.get("year")

        # Extract content
        paragraphs = response.xpath(
            '//div[contains(@class, "td-post-content tagdiv-type")]//p//text()'
        ).getall()
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        content = "\n".join(paragraphs)

        yield {
            "Title": title,
            "URL": link,
            "Year": year,
            "Content": content
        }
