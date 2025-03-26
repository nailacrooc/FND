import scrapy

class Scraper(scrapy.Spider):
    name = "daily_stormer"
    base_url = "https://www.dailystormer.com"
    start_page = 1
    max_pages = 1  # Adjust as needed

    def start_requests(self):
        for page_num in range(self.start_page, self.max_pages + 1):
            page_url = f"{self.base_url}/page/{page_num}/"
            self.logger.info(f"Scraping page: {page_url}")
            yield scrapy.Request(url=page_url, callback=self.parse_page)

    def parse_page(self, response):
        articles = response.xpath('//h2[@class="jeg_post_title"]/a | //h3[@class="jeg_post_title"]/a')

        for article in articles:
            title = article.xpath('text()').get()
            link = article.xpath('@href').get()

            if title and link:
                self.logger.info(f"Found Article: {title} ({link})")
                yield scrapy.Request(
                    url=link,
                    callback=self.parse_article,
                    meta={"title": title.strip(), "link": link}
                )

    def parse_article(self, response):
        title = response.meta["title"]
        link = response.meta["link"]

        content_elements = response.xpath('//div[@class="content-inner  jeg_link_underline"]//p | //div[@class="content-inner  jeg_link_underline"]//h2 | //div[@class="content-inner  jeg_link_underline"]//a | //div[@class="content-inner  jeg_link_underline"]//h3 | //div[@class="content-inner  jeg_link_underline"]//li')
        content = "\n".join([el.xpath("normalize-space(.)").get() for el in content_elements if el.xpath("normalize-space(.)").get()])

        if not content.strip():
            self.logger.warning(f"No content found for: {title} ({link})")
            with open("debug_response.html", "w", encoding="utf-8") as f:
                f.write(response.text)
                self.logger.info("Saved response text for debugging.")

        self.logger.info(f"Scraped Article: {title}\n{content[:200]}...\n{'-'*80}")

        yield {
            "Title": title,
            "URL": link,
            "Content": content
        }
