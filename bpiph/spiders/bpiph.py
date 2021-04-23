import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bpiph.items import Article


class bpiphSpider(scrapy.Spider):
    name = 'bpiph'
    start_urls = ['https://www.bpi.com.ph/newsroom']

    def parse(self, response):
        links = response.xpath('//div[@class="widget-text-list-item"]/a/@href').getall() or response.xpath(
            '//a[text()="read more"]').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if '404' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2//text()').get()
        if title:
            title = title.strip()

        date = response.xpath('(//em)[last()]/text()').get()
        if date:
            date = " ".join(date.split()[2:])

        content = response.xpath('//div[@class="widget-text"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content[2:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
