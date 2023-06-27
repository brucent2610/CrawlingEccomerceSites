import scrapy


class TikiproductapiSpider(scrapy.Spider):
    name = "TikiProductApi"
    allowed_domains = ["tiki.vn"]
    start_urls = ["https://tiki.vn/api/v2/products/198744315"]

    def parse(self, response):
        product = response.json()

        if "id" not in product:
            return

        yield product
