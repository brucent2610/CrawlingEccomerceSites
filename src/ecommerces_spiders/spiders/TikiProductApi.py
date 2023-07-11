import scrapy

from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath

def category_id_transfered(value):
    if(value == None):
        return None
    paths = PurePosixPath(unquote(urlparse(value).path)).parts
    return (paths[-1])

class TikiproductapiSpider(scrapy.Spider):
    name = "TikiProductApi"
    allowed_domains = ["tiki.vn"]
    start_urls = ["https://tiki.vn/api/v2/products/269761"]

    def parse(self, response):
        if response.status == 404:

            product_id = category_id_transfered(response.url)

            yield {
                'id': int(product_id),
                'status': 404
            }
        
        if response.status == 500:

            product_id = category_id_transfered(response.url)

            yield {
                'id': int(product_id),
                'status': 500
            }

        try:
            product = response.json()

            if "id" not in product:
                return

            product['status'] = response.status

            yield product
        
        except Exception as error:

            print("Error json decode", error, response.url)
            print("Response", response.text)

            product_id = category_id_transfered(response.url)

            yield {
                'id': int(product_id),
                'status': response.status,
                'error': str(error),
                'response': response.text
            }
