<<<<<<< HEAD
import scrapy

class Scraper(scrapy.Spider):
    name = "get_real_ph"
    base_url = "https://www.getrealphilippines.com/category/politics"
    start_page = 1
    max_pages = 70  # You can increase this if needed

    custom_settings = {
        'ROBOTSTXT_OBEY': False,  # Allow crawling even if robots.txt fails
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }

    def start_requests(self):
        for page_num in range(self.start_page, self.max_pages + 1):
            page_url = f"{self.base_url}/page/{page_num}/"
            print(f"Scraping page: {page_url}")
            yield scrapy.Request(url=page_url, callback=self.parse_page)

    def parse_page(self, response):
        container = response.xpath('//div[contains(@class, "pb-content-sidebar")]')
        articles = container.xpath('.//h2/a')

        seen_links = set()

        for article in articles:
            title = article.xpath('normalize-space(text())').get()
            link = article.xpath('./@href').get()

            if title and link:
                unique_combination = (link.strip(), title.strip())

                if unique_combination not in seen_links:
                    seen_links.add(unique_combination)
                    print(f"Found Article: {title} ({link})")
                    yield scrapy.Request(
                        url=link.strip(),
                        callback=self.parse_article,
                        meta={"link": link.strip(), "title": title.strip()}
                    )

    def parse_article(self, response):
        title = response.meta["title"]
        link = response.meta["link"]

        # Extract all paragraphs under div.entry-content
        paragraphs = response.xpath('//div[contains(@class, "entry-content")]//p')

        # Skip the last paragraph if there are more than 1 paragraph
        paragraphs = paragraphs[:-1] if len(paragraphs) > 1 else []

        print(f"Article '{title}' has {len(paragraphs)} paragraphs (excluding last one).")

        cleaned_paragraphs = []

        for p in paragraphs:
            text = "".join(p.xpath('.//text()').getall()).strip()
            if text:
                cleaned_paragraphs.append(text)

        content = "\n".join(cleaned_paragraphs)

        print(f"Scraped Article: {title}\n{content[:200]}...\n{'-'*80}")

        yield {
            "Title": title,
            "URL": link,
            "Content": content
        }

    def close(self, reason):
        pass
=======
import scrapy

class Scraper(scrapy.Spider):
    name = "get_real_ph"
    base_url = "https://www.getrealphilippines.com/category/politics"
    start_page = 1
    max_pages = 70  # You can increase this if needed

    custom_settings = {
        'ROBOTSTXT_OBEY': False,  # Allow crawling even if robots.txt fails
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }

    def start_requests(self):
        for page_num in range(self.start_page, self.max_pages + 1):
            page_url = f"{self.base_url}/page/{page_num}/"
            print(f"Scraping page: {page_url}")
            yield scrapy.Request(url=page_url, callback=self.parse_page)

    def parse_page(self, response):
        container = response.xpath('//div[contains(@class, "pb-content-sidebar")]')
        articles = container.xpath('.//h2/a')

        seen_links = set()

        for article in articles:
            title = article.xpath('normalize-space(text())').get()
            link = article.xpath('./@href').get()

            if title and link:
                unique_combination = (link.strip(), title.strip())

                if unique_combination not in seen_links:
                    seen_links.add(unique_combination)
                    print(f"Found Article: {title} ({link})")
                    yield scrapy.Request(
                        url=link.strip(),
                        callback=self.parse_article,
                        meta={"link": link.strip(), "title": title.strip()}
                    )

    def parse_article(self, response):
        title = response.meta["title"]
        link = response.meta["link"]

        # Extract all paragraphs under div.entry-content
        paragraphs = response.xpath('//div[contains(@class, "entry-content")]//p')

        # Skip the last paragraph if there are more than 1 paragraph
        paragraphs = paragraphs[:-1] if len(paragraphs) > 1 else []

        print(f"Article '{title}' has {len(paragraphs)} paragraphs (excluding last one).")

        cleaned_paragraphs = []

        for p in paragraphs:
            text = "".join(p.xpath('.//text()').getall()).strip()
            if text:
                cleaned_paragraphs.append(text)

        content = "\n".join(cleaned_paragraphs)

        print(f"Scraped Article: {title}\n{content[:200]}...\n{'-'*80}")

        yield {
            "Title": title,
            "URL": link,
            "Content": content
        }

    def close(self, reason):
        pass
>>>>>>> d0050842680606b01ed9a22a1139e3a3f71243dd
