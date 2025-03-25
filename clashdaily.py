import scrapy

class ClashDailySpider(scrapy.Spider):
    name = "clashdaily"
    allowed_domains = ["clashdaily.com"]
    start_urls = ["https://clashdaily.com/page/1/"]

    def parse(self, response):
        # Extract current page number
        page_number = self.extract_page_number(response.url)
        
        # Extract all article links from different sections
        article_links = response.css("h2.post-title a::attr(href)").getall()
        thumb_links = response.css("h2.thumb-title a::attr(href)").getall()
        
        for link in set(article_links + thumb_links):  # Remove duplicates
            if link:
                yield response.follow(link.strip(), self.parse_article, meta={"page_number": page_number})
        
        # Extract pagination links and follow next pages
        next_page = response.css("a.pages-nav-item[title]:last-of-type::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse, meta={"page_number": page_number + 1})

    def parse_article(self, response):
        yield {
            "title": response.css("h1.post-title::text").get(default="").strip(),
            "content": "\n".join(response.css("div.entry-content p::text").getall()).strip(),
            "thumb_title": response.css("h2.thumb-title::text").get(default="").strip(),
            "page_number": response.meta.get("page_number", 1)
        }
    
    def extract_page_number(self, url):
        parts = url.rstrip("/").split("/")
        if "page" in parts:
            index = parts.index("page")
            if index + 1 < len(parts) and parts[index + 1].isdigit():
                return int(parts[index + 1])
        return 1