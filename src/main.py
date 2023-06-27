import os

from time import sleep

from scrapy import cmdline
from Database import Database
from ecommerces_spiders.spiders.TikiPage import TikipageSpider
from ecommerces_spiders.spiders.TikiCategoryApi import TikicategoryapiSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

print("Running", os.getenv("ENV"))

database = Database()
mongodb = database.initialize()

LIMIT = os.getenv("LIMIT")

if __name__ == "__main__": 

    setting = get_project_settings()

    process = CrawlerProcess(setting)
    process.crawl(TikipageSpider)

    collection = mongodb["categories"]
    
    categories = collection.find({
        '$expr': { 
            '$ne': [ 
                "$last_page", 
                "$current_page" 
            ] 
        },
        {
            'total': {
                '$gt': 0
            }
        }
        # '$expr': {'$gt': [{ '$subtract': ['$last_page', 1]} ,'$current_page']},
        # '$expr': {'$eq': [{ '$subtract': ['$last_page', 1]} ,'$current_page']},
        # 'last_page': {
        #     '$lt': 20
        # }
    }).limit(500)

    urls = []
    for category in categories:
        print(category)
        if "last_page" not in category or "current_page" not in category:
            continue
        if category["last_page"] <= 0:
            continue
        if category["current_page"] > category["last_page"]:
            continue
        for i in range(int(category["current_page"]), int(category["last_page"]) + 1):
            print(i)
            urls.append("https://tiki.vn/api/personalish/v1/blocks/listings?limit=100&aggregations=2&category="+ str(category["category_id"]) +"&page=" + str(i))

    process.crawl(TikicategoryapiSpider, start_urls=urls)
    process.start()

    if(database is not None and mongodb is not None): 
        database.close(mongodb)