import scrapy

class Scraper(scrapy.Spider):
    name = "100_percent_fedup"
    base_url = "https://100percentfedup.com"
    start_page = 1
    max_pages = 634  # Adjust as needed

    def start_requests(self):
        for page_num in range(self.start_page, self.max_pages + 1):
            page_url = f"{self.base_url}/page/{page_num}/"
            print(f"Scraping page: {page_url}")
            yield scrapy.Request(url=page_url, callback=self.parse_page)

    def parse_page(self, response):
        # Select articles from all four relevant sections
        articles = response.xpath('//a[@class="wpdev-main-post-title"] | '
                                  '//a[@class="wpdev-trending-grid-title"] | '
                                  '//a[@class="wpdev-post-grid-title"]')

        popular_articles = response.xpath('//ul[@class="wpp-list"]//h4/a')

        seen_links = set()  # Track unique article links

        # Scrape regular and trending articles
        for article in articles:
            link = article.xpath('./@href').get()
            title = article.xpath('./h2/text()').get()

            if link and title:
                link, title = link.strip(), title.strip()

                if link not in seen_links:  # Avoid duplicate scraping
                    seen_links.add(link)
                    print(f"Found Article: {title} ({link})")
                    yield scrapy.Request(
                        url=link,
                        callback=self.parse_article,
                        meta={"link": link, "title": title}
                    )

        # Scrape popular articles from wpp-list
        for article in popular_articles:
            link = article.xpath('./@href').get()
            title = article.xpath('./text()').get()

            if link and title:
                link, title = link.strip(), title.strip()

                if link not in seen_links:  # Avoid duplicate scraping
                    seen_links.add(link)
                    print(f"Found Popular Article: {title} ({link})")
                    yield scrapy.Request(
                        url=link,
                        callback=self.parse_article,
                        meta={"link": link, "title": title}
                    )

    def parse_article(self, response):
        title = response.meta["title"]
        link = response.meta["link"]

        paragraphs = response.xpath('//p//text()').getall()
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        # Remove the first paragraph (optional, depending on article structure)
        paragraphs = paragraphs[1:] if len(paragraphs) > 1 else paragraphs

        # Remove the last 5 paragraphs (optional, if they contain unwanted content)
        if len(paragraphs) > 5:
            paragraphs = paragraphs[:-5]

        content = "\n".join(paragraphs)

        print(f"Scraped Article: {title}\n{content[:200]}...\n{'-'*80}")

        yield {
            "Title": title,
            "URL": link,
            "Content": content
        }
