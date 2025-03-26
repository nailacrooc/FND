import scrapy

class Scraper(scrapy.Spider):
    name = "now8news"
    base_url = "https://now8news.com"
    start_page = 1
    max_pages = 35  # Adjust as needed

    def start_requests(self):
        for page_num in range(self.start_page, self.max_pages + 1):
            page_url = f"{self.base_url}/page/{page_num}/"
            print(f"Scraping page: {page_url}")
            yield scrapy.Request(url=page_url, callback=self.parse_page)

    def parse_page(self, response):
        articles = response.xpath('//a[@rel="bookmark"]')

        seen_links = set()

        for article in articles:
            title = article.xpath('./text()').get()
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

        paragraphs = response.xpath('//p')
        num_paragraphs = len(paragraphs)  # Count total <p> elements
        print(f"Article '{title}' has {num_paragraphs} paragraphs.")

        cleaned_paragraphs = []

        for p in paragraphs:
            text = "".join(p.xpath('.//text()').getall()).strip()  
            if text:
                cleaned_paragraphs.append(text)

        content = "\n".join(cleaned_paragraphs)  # No limit on number of paragraphs

        print(f"Scraped Article: {title}\n{content[:200]}...\n{'-'*80}")

        yield {
            "Title": title,
            "URL": link,
            "Content": content
        }

    def close(self, reason):
        pass
