import scrapy

class Scraper(scrapy.Spider):
    name = "daily_infobox"
    base_url = "https://dailyinfobox.com"
    start_page = 1
    max_pages = 4  # Adjust as needed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_links = set()  # Track seen articles globally

    def start_requests(self):
        for page_num in range(self.start_page, self.max_pages + 1):
            page_url = f"{self.base_url}/page/{page_num}/"
            self.logger.info(f"Scraping page: {page_url}")
            yield scrapy.Request(url=page_url, callback=self.parse_page)

    def parse_page(self, response):
        articles = response.xpath('//a[@rel="bookmark"]')

        for article in articles:
            title = article.xpath('./text()').get()
            link = article.xpath('./@href').get()

            if title and link:
                unique_combination = (link.strip(), title.strip())

                if unique_combination not in self.seen_links:
                    self.seen_links.add(unique_combination)
                    self.logger.info(f"Found Article: {title} ({link})")
                    yield scrapy.Request(
                        url=link.strip(),
                        callback=self.parse_article,
                        meta={"link": link.strip(), "title": title.strip()}
                    )

    def parse_article(self, response):
        title = response.meta["title"]
        link = response.meta["link"]

        paragraphs = response.xpath('//div[@class="entry-content"]//p')  # Corrected XPath
        num_paragraphs = len(paragraphs)  
        self.logger.info(f"Article '{title}' has {num_paragraphs} paragraphs.")

        cleaned_paragraphs = [
            "".join(p.xpath('.//text()').getall()).strip()
            for p in paragraphs if "".join(p.xpath('.//text()').getall()).strip()
        ]

        content = "\n".join(cleaned_paragraphs)  

        self.logger.info(f"Scraped Article: {title}\n{content[:200]}...\n{'-'*80}")

        yield {
            "Title": title,
            "URL": link,
            "Content": content
        }

    def close(self, reason):
        self.logger.info(f"Spider closed: {reason}")
