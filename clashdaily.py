import scrapy

class ClashDailySpider(scrapy.Spider):
    name = "clashdaily"
    base_url = "https://clashdaily.com"
    start_page = 1
    max_pages = 5  # Adjust as needed

    def start_requests(self):
        for page_num in range(self.start_page, self.max_pages + 1):
            page_url = f"{self.base_url}/page/{page_num}/"
            print(f"Scraping page: {page_url}")
            yield scrapy.Request(url=page_url, callback=self.parse_page)

    def parse_page(self, response):
        article_links = response.css("h2.post-title a::attr(href)").getall()
        thumb_links = response.css("h2.thumb-title a::attr(href)").getall()

        for link in set(article_links + thumb_links):  # Remove duplicates
            if link:
                yield scrapy.Request(
                    url=link.strip(),
                    callback=self.parse_article,
                    meta={"link": link.strip()}
                )

    def parse_article(self, response):
        title = response.css("h1.post-title::text").get(default="").strip()
        link = response.meta["link"]

        paragraphs = response.css("div.entry-content p::text").getall()
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