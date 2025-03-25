import scrapy

class Scraper(scrapy.Spider):
    name = "daily_headline"
    base_url = "https://dailyheadlines.net"
    start_page = 1
    max_pages = 1000  # Adjust as needed
    
    def start_requests(self):
        for page_num in range(self.start_page, self.max_pages + 1):
            page_url = f"{self.base_url}/page/{page_num}/"
            print(f"Scraping page: {page_url}")
            yield scrapy.Request(url=page_url, callback=self.parse_page)

    def parse_page(self, response):
        articles = response.xpath('//a[@rel="bookmark"]')

        seen_links = set()  # To track unique combinations of links and titles

        for article in articles:
            title = article.xpath('./text()').get()
            link = article.xpath('./@href').get()

            # Remove duplicates by combining link and title in a set
            if title and link:
                unique_combination = set([link.strip(), title.strip()])

                # Only scrape the article if it's a new unique combination
                if not any(item in seen_links for item in unique_combination):
                    seen_links.update(unique_combination)  # Add both link and title to the set
                    print(f"Found Article: {title} ({link})")
                    yield scrapy.Request(
                        url=link.strip(),
                        callback=self.parse_article,
                        meta={"link": link.strip(), "title": title.strip()}
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

    def close(self, reason):
        """This method is automatically called when the spider closes, if you want to add any clean-up."""
        pass
