import scrapy

from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath

def category_id_transfered(value):
    if(value == None):
        return None
    paths = PurePosixPath(unquote(urlparse(value).path)).parts
    return (paths[-1])

class TikipageSpider(scrapy.Spider):
    name = "TikiPage"
    allowed_domains = ["tiki.vn"]
    start_urls = ["https://tiki.vn"]

    def parse(self, response):

        categories = []

        items = response.css(".styles__StyledCategory-sc-17y817k-1")

        for item in items:

            main_category_url = item.css(".styles__FooterSubheading-sc-32ws10-5 a::attr(\"href\")").extract_first()
            main_category_title = item.css(".styles__FooterSubheading-sc-32ws10-5 a::text").extract_first()
            main_category_id = category_id_transfered(main_category_url)

            if(main_category_id == None or main_category_id[0] != "c"):
                continue

            for sub_item in item.css("p a"):

                sub_category_url = sub_item.css("::attr(\"href\")").extract_first()
                sub_category_title = sub_item.css("::text").extract_first()
                sub_category_id = category_id_transfered(sub_category_url)

                if(sub_category_id == None or sub_category_id[0] != "c"):
                    continue

                sub_category_id_int = int(sub_category_id.replace("c", ""))

                categories.append({
                    "category_id": sub_category_id_int,
                    "title": sub_category_title,
                    "url": sub_category_url,
                    "api_url": "https://tiki.vn/api/personalish/v1/blocks/listings?page=#PAGE#&limit=40&aggregations=2&category=" + str(sub_category_id_int)
                })

            main_category_id_int = int(main_category_id.replace("c", ""))

            categories.append({
                "category_id": main_category_id_int,
                "title": main_category_title,
                "url": main_category_url,
                "api_url": "https://tiki.vn/api/personalish/v1/blocks/listings?page=#PAGE#&limit=40&aggregations=2&category=" + str(main_category_id_int),
                "parent_id": 0
            })

        yield {
            'categories': categories
        }
