import scrapy

class HealthSpider(scrapy.Spider):
    name = "health"
    allowed_domains = ["naturalnews.com"]

    # Set how many listing pages to scrape
    max_pages = 109

    def start_requests(self):
        base_url = "https://www.naturalnews.com/category/health/page/{}"
        for page in range(1, self.max_pages + 1):
            url = base_url.format(page)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        headlines = response.css('div.Headline')

        for headline in headlines:
            a_tag = headline.css('a')
            if a_tag:
                relative_url = a_tag.attrib.get('href')
                url = response.urljoin(relative_url)
                text = a_tag.css('::text').get().strip()

                yield scrapy.Request(
                    url=url,
                    callback=self.parse_article,
                    meta={'text': text, 'url': url}
                )

    def parse_article(self, response):
        text = response.meta['text']
        url = response.meta['url']

        # Extract publish date
        date = response.css('div#AuthorInfo::text').get()
        if date:
            date = date.strip()
        else:
            date = ""

        # Extract all visible text under #Article including <a>, <em>, etc.
        article_div = response.xpath('//div[@id="Article"]')
        content_parts = article_div.xpath('.//text()').getall()
        content = " ".join([part.strip() for part in content_parts if part.strip()])

        yield {
            'text': text,
            'url': url,
            'date': date,
            'content': content
        }
