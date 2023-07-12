import os
import sys

from time import sleep
from datetime import datetime

from scrapy import cmdline
from Database import MongoDB
from ecommerces_spiders.spiders.TikiProductApi import TikiproductapiSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

print("Running", os.getenv("ENV"))

database = MongoDB()
mongodb = database.initialize()

LIMIT = os.getenv("LIMIT")
SKIP = os.getenv("SKIP")

if __name__ == "__main__": 

    setting = get_project_settings()
    process = CrawlerProcess(setting)

    collection = mongodb["products"]

    # 1. Query when first time check and track point where to crawl
    # query = {"is_crawl_detail":{"$ne": True}}

    # 2. Query after there is issue with Capcha
    # query = {"error":"Expecting value: line 1 column 1 (char 0)"}

    # 3. Query recheck status not 200
    query = {"status": {"$ne": 200}}
    
    products = collection.find(query).skip(int(SKIP)).limit(int(LIMIT))

    # 16:00 - July 1, 2023
    # Process the record
    urls = []
    for product in products:
        if "id" not in product:
            continue
        urls.append("https://tiki.vn/api/v2/products/" + str(product["id"]))

    print(urls)

    process.crawl(TikiproductapiSpider, start_urls=urls)
    process.start()

    if len(urls) <= 0:
        if(database is not None and mongodb is not None): 
            database.close(mongodb)
        sys.exit()

    process.crawl(TikicategoryapiSpider, start_urls=urls)
    process.start()

    sleep(0.5)
    os.execl(sys.executable, sys.executable, *sys.argv)