import scrapy

class Scraper(scrapy.Spider):
    name = "rochdale_herald"
    start_urls = ["https://rochdaleherald.co.uk/other/health/"]

    def parse(self, response):
        # Scope to td_module_11 td_module_wrap td-animation-stack for the initial articles
        container = response.xpath('//div[contains(@class, "td_module_11 td_module_wrap td-animation-stack")]')

        # Extract article links from within the container
        article_links = container.xpath('.//a[@href and @title]')

        for article in article_links:
            title = article.xpath('./@title').get()
            link = article.xpath('./@href').get()
            if not (title and link):
                continue

            full_url = response.urljoin(link)
            yield scrapy.Request(
                url=full_url,
                callback=self.parse_article,
                meta={"title": title.strip(), "link": full_url}
            )

        # Look for the "Load More" button inside td-load-more-wrap td-load-more-infinite-wrap
        load_more_button = response.xpath('//div[contains(@class, "td-load-more-wrap td-load-more-infinite-wrap")]//a[contains(@href, "#")]')

        if load_more_button:
            # Try to find the next set of articles by making a request to scrape again
            yield scrapy.Request(
                url=response.url,
                callback=self.parse
            )

    def parse_article(self, response):
        title = response.meta["title"]
        link = response.meta["link"]

        paragraphs = response.xpath(
            '//div[contains(@class, "td-post-content")]//p//text()'
        ).getall()
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        content = "\n".join(paragraphs)

        yield {
            "Title": title,
            "URL": link,
            "Content": content
        }
