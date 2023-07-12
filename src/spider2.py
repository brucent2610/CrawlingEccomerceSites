# Crawl the categories and the sub inside

import os

from time import sleep

from scrapy import cmdline
from Database import MongoDB
from ecommerces_spiders.spiders.TikiPage import TikipageSpider
from ecommerces_spiders.spiders.TikiCategoryApi import TikicategoryapiSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

print("Running", os.getenv("ENV"))

database = MongoDB()
mongodb = database.initialize()

LIMIT = os.getenv("LIMIT")

if __name__ == "__main__": 

    setting = get_project_settings()

    process = CrawlerProcess(setting)
    process.crawl(TikipageSpider)

    collection = mongodb["categories"]
    
    categories = collection.find({
        'current_page': {
            '$exists': False
        }
    }).limit(int(LIMIT))

    urls = []
    for category in categories:
        urls.append("https://tiki.vn/api/personalish/v1/blocks/listings?limit=200&aggregations=2&category="+ str(category["category_id"]) +"&page=1")

    if len(urls) <= 0:
        if(database is not None and mongodb is not None): 
            database.close(mongodb)
        sys.exit()

    process.crawl(TikicategoryapiSpider, start_urls=urls)
    process.start()

    sleep(0.5)
    os.execl(sys.executable, sys.executable, *sys.argv)