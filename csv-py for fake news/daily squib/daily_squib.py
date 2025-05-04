import scrapy

class Scraper(scrapy.Spider):
    name = "the_poke"
    base_url = "https://www.dailysquib.co.uk/category/entertainment"
    start_page = 1
    max_pages = 80  # Increase this to crawl more pages

    def start_requests(self):
        for page_num in range(self.start_page, self.max_pages + 1):
            page_url = f"{self.base_url}/page/{page_num}/"
            self.logger.info(f"Scraping page: {page_url}")
            yield scrapy.Request(url=page_url, callback=self.parse_page)

    def parse_page(self, response):
        # XPath for tdi_65 container
        xpath_tdi_65 = (
            '//div[contains(@class, "td_block_wrap") and contains(@class, "tdb_loop") '
            'and contains(@class, "tdi_65") and contains(@class, "tdb-numbered-pagination") '
            'and contains(@class, "td_with_ajax_pagination") and contains(@class, "tdb-category-loop-posts")]'
        )

        # XPath for tdi_55 container
        xpath_tdi_55 = '//div[@id="tdi_55" and contains(@class, "td_block_inner")]'

        # Collect <a> elements from both containers, excluding any inside pagination
        articles_tdi_65 = response.xpath(f'{xpath_tdi_65}//a[not(ancestor::div[contains(@class, "page-nav")])]')        
        articles_tdi_55 = response.xpath(f'{xpath_tdi_55}//a[not(ancestor::div[contains(@class, "page-nav")])]')

        all_articles = articles_tdi_65 + articles_tdi_55

        for article in all_articles:
            headline = article.xpath('.//text()').get()
            headline = headline.strip() if headline else None

            link = article.xpath('./@href').get()

            if not (headline and link):
                continue

            full_url = response.urljoin(link)

            yield scrapy.Request(
                url=full_url,
                callback=self.parse_article,
                meta={"headline": headline, "link": full_url}
            )

    def parse_article(self, response):
        headline = response.meta["headline"]
        link = response.meta["link"]

        # Extract headline from h3 inside tdi_65 if available
        headline_from_h3 = response.xpath('//div[@id="tdi_65"]//h3//text()').get()
        if headline_from_h3:
            headline_from_h3 = headline_from_h3.strip()

        # Get all direct <p> elements under the specified container
        paragraphs = response.xpath(
            '//div[contains(@class, "tdb-block-inner") and contains(@class, "td-fix-index")]/p'
        )

        content = []
        for index, p in enumerate(paragraphs):
            if index == 0:
                continue  # Skip the first <p>

            # Skip if any nested element contains "Read More"
            if p.xpath('.//*[contains(text(), "Read More")]'):
                continue

            nested_elements = p.xpath('.//*[not(self::p)]')

            # Handle text accordingly
            if nested_elements:
                text = " ".join(p.xpath('.//text()').getall()).strip()
            else:
                text = p.xpath('.//text()').get()
                text = text.strip() if text else ""

            if text:
                content.append(text)

        content_text = "\n".join(content)

        # Extract year from datetime
        year = response.xpath('//time[contains(@class, "entry-date updated td-module-date")]/@datetime').get()
        if year:
            year = year[:4]

        yield {
            "Headline": headline_from_h3 or headline,
            "URL": link,
            "Year": year,
            "Content": content_text
        }
