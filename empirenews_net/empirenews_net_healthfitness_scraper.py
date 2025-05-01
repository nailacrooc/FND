import scrapy

class Scraper(scrapy.Spider):
    name = "empire_health"
    allowed_domains = ["empirenews.net"]
    start_urls = ["https://empirenews.net/category/healthfitness/"]
    max_pages = 2  # Set a reasonable max page limit
    page_count = 0

    def parse(self, response):
        self.page_count += 1
        self.logger.info(f"Scraping page {self.page_count}: {response.url}")

        # Extract article links
        articles = response.xpath('//a[@rel="bookmark"]')
        for article in articles:
            title = article.xpath('text()').get()
            link = article.xpath('@href').get()
            if title and link:
                yield scrapy.Request(
                    url=link,
                    callback=self.parse_article,
                    meta={"title": title.strip(), "link": link}
                )

        # Find and follow the "Older posts" link
        if self.page_count < self.max_pages:
            next_page = response.xpath('//a[contains(text(), "Older posts")]/@href').get()
            if next_page and "/category/healthfitness/" in next_page:
                yield response.follow(next_page, callback=self.parse)

    def parse_article(self, response):
        title = response.meta["title"]
        link = response.meta["link"]

        # Extract published date
        published_date = response.xpath('//time/@datetime').get()
        if not published_date:
            published_date = response.xpath('//time/text()').get()

        # Extract article paragraphs
        paragraphs = response.xpath('//p//text()').getall()
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        # Clean up: remove first paragraph and last 5 (often boilerplate or ads)
        if paragraphs:
            paragraphs = paragraphs[1:]
        if len(paragraphs) > 5:
            paragraphs = paragraphs[:-5]

        content = "\n".join(paragraphs)

        yield {
            "Title": title,
            "URL": link,
            "PublishedDate": published_date,
            "Content": content
        }
