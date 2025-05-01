import scrapy

class Scraper(scrapy.Spider):
    name = "empire_news"
    base_url = "https://empirenews.net"
    start_page = 1
    max_pages = 279  # Adjust as needed

    def start_requests(self):
        for page_num in range(self.start_page, self.max_pages + 1):
            page_url = f"{self.base_url}/page/{page_num}/"
            print(f"Scraping page: {page_url}")
            yield scrapy.Request(url=page_url, callback=self.parse_page)

    def parse_page(self, response):
        articles = response.xpath('//a[@title="Read more"]')

        for article in articles:
            title = article.xpath('./text()').get()
            link = article.xpath('./@href').get()

            if title and link:
                print(f"Found Article: {title} ({link})")
                yield scrapy.Request(
                    url=link,
                    callback=self.parse_article,
                    meta={"title": title.strip(), "link": link}
                )

    def parse_article(self, response):
        title = response.meta["title"]
        link = response.meta["link"]

        paragraphs = response.xpath('//p//text()').getall()
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        # Remove the first paragraph
        paragraphs = paragraphs[1:]
        
        # Remove the last 5 paragraphs
        if len(paragraphs) > 5:
            paragraphs = paragraphs[:-5]

        content = "\n".join(paragraphs)

        print(f"Scraped Article: {title}\n{content[:200]}...\n{'-'*80}")

        yield {
            "Title": title,
            "URL": link,
            "Content": content
        }

