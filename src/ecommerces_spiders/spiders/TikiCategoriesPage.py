import scrapy

from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath

def category_id_transfered(value):
    if(value == None):
        return None
    paths = PurePosixPath(unquote(urlparse(value).path)).parts
    return (paths[-1])

class TikicategoriespageSpider(scrapy.Spider):
    name = "TikiCategoriesPage"
    allowed_domains = ["tiki.vn"]
    start_urls = ["https://tiki.vn"]

    def parse_sub(self, response, item, lv):
        json_response = response.json()

        if "category_id" not in item:
            return

        print("Running parse_sub" + str(lv) + " main cat " + str(item["category_id"]))

        if "filters" not in json_response:
            return

        if "data" not in json_response:
            return

        raw_categories = []
        for fil in json_response['filters']:
            if fil["query_name"] == "category" and "values" in fil:
                raw_categories = fil["values"]
                break
        
        categories = []
        if(len(raw_categories) > 0):
            for raw_cat in raw_categories:

                category_id_int = raw_cat["query_value"]
                category_title = raw_cat["display_value"]
                category_url = "https://tiki.vn" + raw_cat["url_path"]

                api_url = "https://tiki.vn/api/personalish/v1/blocks/listings?page=#PAGE#&limit=40&aggregations=2&category=" + str(category_id_int)

                category = {
                    "category_id": category_id_int,
                    "title": category_title,
                    "url": category_url,
                    "api_url": api_url,
                    "parent_id": int(item["category_id"]),
                    "reffer": response.url
                }

                categories.append(category)

                yield scrapy.Request(api_url.replace("#PAGE#", "1"), callback=self.parse_sub, cb_kwargs=dict(item=category,lv=lv+1))

        paging = {}
        
        if "paging" in json_response:
            paging = json_response['paging']

        yield {
            'main_category_id': item['category_id'],
            'paging': paging,
            'categories': categories
        }

    def parse(self, response):
        categories = []

        items = response.css(".styles__StyledCategory-sc-17y817k-1")

        for item in items:

            main_category_url = item.css(".styles__FooterSubheading-sc-32ws10-5 a::attr(\"href\")").extract_first()
            main_category_title = item.css(".styles__FooterSubheading-sc-32ws10-5 a::text").extract_first()
            main_category_id = category_id_transfered(main_category_url)

            if(main_category_id == None or main_category_id[0] != "c"):
                continue

            main_category_id_int = int(main_category_id.replace("c", ""))

            # if(main_category_id_int != 1789):
            #     continue

            api_url = "https://tiki.vn/api/personalish/v1/blocks/listings?page=#PAGE#&limit=40&aggregations=2&category=" + str(1520)

            category = {
                "category_id": main_category_id_int,
                "title": main_category_title,
                "url": main_category_url,
                "api_url": api_url,
                "reffer": response.url
            }

            categories.append(category)

            yield scrapy.Request(api_url.replace("#PAGE#", "1"), callback=self.parse_sub, cb_kwargs=dict(item=category,lv=1))

        yield {
            'categories': categories
        }
