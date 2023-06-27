import scrapy
from urllib.parse import urlparse, parse_qs

class TikicategoryapiSpider(scrapy.Spider):
    name = "TikiCategoryApi"
    allowed_domains = ["tiki.vn"]
    start_urls = ["https://tiki.vn/api/personalish/v1/blocks/listings?page=1&limit=40&aggregations=2&category=11601"]

    # def __init__(self, cat=0, pages="1,100", limit=100):
    #     self.category_id = int(cat)
    #     rangePages = pages.split(",")
    #     for i in range(int(rangePages[0]), int(rangePages[1]) + 1):
    #         list_url = "https://tiki.vn/api/personalish/v1/blocks/listings?limit="+ str(limit) +"&aggregations=2&category="+ str(cat) +"&page=" + str(i)
    #         print(list_url)
    #         self.start_urls.append(list_url)

    def parse(self, response):

        json_response = response.json()

        if "data" not in json_response:
            return

        products = json_response['data']

        raw_categories = []
        if "filters" in json_response:
            for fil in json_response['filters']:
                if fil["query_name"] == "category" and "values" in fil:
                    raw_categories = fil["values"]
                    break

        main_category_id = 0
        parse_result = urlparse(response.url)
        dict_result = parse_qs(parse_result.query)
        main_category_id = dict_result["category"][0]
        
        categories = []
        if(len(raw_categories) > 0):
            for raw_cat in raw_categories:

                category_id_int = raw_cat["query_value"]
                category_title = raw_cat["display_value"]
                category_url = "https://tiki.vn" + raw_cat["url_path"]

                categories.append({
                    "category_id": category_id_int,
                    "title": category_title,
                    "url": category_url,
                    "api_url": "https://tiki.vn/api/personalish/v1/blocks/listings?page=#PAGE#&limit=40&aggregations=2&category=" + str(category_id_int),
                    "reffer": response.url,
                    "parent_id": int(main_category_id)
                })

        paging = {}
        
        if "paging" in json_response:
            paging = json_response['paging']

        yield {
            'main_category_id': int(main_category_id),
            'paging': paging,
            'categories': categories,
            # 'products': []
            'products': products
        }


