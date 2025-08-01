import scrapy


class AdspiderSpider(scrapy.Spider):
    name = "adspider"
    allowed_domains = ["www.pararius.nl"]
    start_urls = ["https://www.pararius.nl/huurwoningen/nederland"]

    def parse(self, response):
        pass
