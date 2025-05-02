import scrapy

class Scraper(scrapy.Spider):
    name = "the_poke"
    base_url = "https://www.thepoke.com/category/politics/"
    start_page = 1
    max_pages = 2  # Increase this to crawl more pages

    def start_requests(self):
        for page_num in range(self.start_page, self.max_pages + 1):
            page_url = f"{self.base_url}/page/{page_num}/"
            self.logger.info(f"Scraping page: {page_url}")
            yield scrapy.Request(url=page_url, callback=self.parse_page)

    def parse_page(self, response):
        # Extracting article links from the boxframe.archive section
        articles = response.xpath('//div[contains(@class, "boxframe archive")]//a')

        for article in articles:
            title = article.xpath('.//p//text()').get()
            link = article.xpath('./@href').get()

            if not (title and link):
                continue

            full_url = response.urljoin(link)

            yield scrapy.Request(
                url=full_url,
                callback=self.parse_article,
                meta={"title": title.strip(), "link": full_url}
            )

    def parse_article(self, response):
        title = response.meta["title"]
        link = response.meta["link"]

        # Get the first 3 <p> tags inside the article body
        paragraphs = response.xpath(
            '(//div[contains(@class, "entry normal js-article-body")]//p)[position() <= 3]//text()'
        ).getall()
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        content = "\n".join(paragraphs)

        # Extract date (month, day, and year) from <p class="byline">, ignore <a> tags inside it
        month, day, year = None, None, None
        byline_text = response.xpath('//div[contains(@class, "post")]//p[contains(@class, "byline")]//text()[not(parent::a)]').getall()
        if byline_text:
            # Combine the byline text into a single string
            byline_text = " ".join(byline_text).strip()

            # Try to extract the month, day, and year from the text
            words = byline_text.split()
            for word in words:
                if word.isdigit():
                    if len(word) == 2 and not month:
                        month = int(word)
                    elif len(word) == 2 and not day:
                        day = int(word)
                    elif len(word) == 4 and not year:
                        year = int(word)

            # Skip articles from before 2020 and stop further scraping if found
            if year is not None and year < 2020:
                self.logger.info(f"Stopping the spider due to article from {year}: {link}")
                self.crawler.engine.close_spider(self, "Year before 2020 encountered")
                return

        # Format the date as 'MM-DD-YYYY' if all parts are available
        if month and day and year:
            year = f"{month:02d}-{day:02d}-{year}"

        yield {
            "Title": title,
            "Headline": title,
            "URL": link,
            "Year": year,  # Combined month, day, and year here
            "Content": content
        }