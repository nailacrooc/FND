import scrapy

class Scraper(scrapy.Spider):
    name = "empire_entertainment"
    allowed_domains = ["empirenews.net"]
    start_urls = ["https://empirenews.net/category/entertainment/page/50/"]
    max_pages = 100  # Adjust as needed
    page_count = 0

    def parse(self, response):
        self.page_count += 1
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

        # Correct pagination: look for "Older posts" link
        if self.page_count < self.max_pages:
            next_page = response.xpath('//a[contains(text(), "Older posts")]/@href').get()
            if next_page and '/category/entertainment/' in next_page and '/video/' not in next_page:
                yield response.follow(next_page, callback=self.parse)

    def parse_article(self, response):
        title = response.meta["title"]
        link = response.meta["link"]

        # Only proceed if article has 'Entertainment' category
        categories = response.xpath('//span[@class="cat-links"]/a/text()').getall()
        if "Entertainment" not in [cat.strip() for cat in categories]:
            return  # Skip articles not tagged as Entertainment

        published_date = response.xpath('//time/@datetime').get()
        if not published_date:
            published_date = response.xpath('//time/text()').get()

        paragraphs = response.xpath('//p//text()').getall()
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

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
