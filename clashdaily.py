import scrapy

class ClashDailySpider(scrapy.Spider):
    name = "clashdaily_scraper"
    base_url = "https://clashdaily.com"
    start_page = 1
    max_pages = 432  # Adjust as needed

    def start_requests(self):
        for page_num in range(self.start_page, self.max_pages + 1):
            page_url = f"{self.base_url}/page/{page_num}/"
            self.logger.info(f"Scraping page: {page_url}")
            yield scrapy.Request(url=page_url, callback=self.parse_page)

    def parse_page(self, response):
        articles = response.css("h2.post-title a, h2.thumb-title a")
        
        for article in articles:
            title = article.css("::text").get()
            link = article.css("::attr(href)").get()

            if title and link:
                self.logger.info(f"Found Article: {title} ({link})")
                yield scrapy.Request(
                    url=link.strip(),
                    callback=self.parse_article,
                    meta={"title": title.strip(), "link": link.strip()}
                )

    def parse_article(self, response):
        title = response.meta["title"]
        link = response.meta["link"]

        content_elements = response.css("div.entry-content p::text").getall()
        content = "\n".join([text.strip() for text in content_elements if text.strip()])

        if not content:
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
