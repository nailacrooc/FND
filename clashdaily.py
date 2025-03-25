import scrapy
import re

class ClashDailySpider(scrapy.Spider):
    name = "clashdaily"
    allowed_domains = ["clashdaily.com"]
    start_urls = ["https://clashdaily.com/page/1/"]

    def parse(self, response):
        # Extract current page number
        page_number = self.get_page_number(response.url)
        
        # Extract all article links from different sections
        article_links = response.css("h2.post-title a::attr(href)").getall()
        thumb_links = response.css("h2.thumb-title a::attr(href)").getall()
        
        for link in set(article_links + thumb_links):  # Remove duplicates
            if link:
                yield response.follow(link.strip(), self.parse_article, meta={"page_number": page_number})
        
        # Follow next pages up to page 1919
        if page_number < 1919:
            next_page = f"https://clashdaily.com/page/{page_number + 1}/"
            yield response.follow(next_page, self.parse, meta={"page_number": page_number + 1})

    def parse_article(self, response):
        yield {
            "title": response.css("h1.post-title::text").get(default="").strip(),
            "content": "\n".join(response.css("div.entry-content p::text").getall()).strip(),
            "thumb_title": response.css("h2.thumb-title::text").get(default="").strip(),
            "page_number": response.meta.get("page_number", 1)
        }
    
    def get_page_number(self, url):
        match = re.search(r"page/(\d+)/", url)
        return int(match.group(1)) if match else 1