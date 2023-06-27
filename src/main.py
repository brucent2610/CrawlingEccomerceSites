import os

from time import sleep

from scrapy import cmdline
from Database import Database
from ecommerces_spiders.spiders.TikiProductApi import TikiproductapiSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

print("Running", os.getenv("ENV"))

database = Database()
mongodb = database.initialize()

LIMIT = os.getenv("LIMIT")

if __name__ == "__main__": 

    setting = get_project_settings()
    process = CrawlerProcess(setting)

    collection = mongodb["products"]
    query = {
        'is_crawl_detail': {
            '$ne': True
        }
    }
    
    products = collection.find(query).limit(2)

    test = 0
    while products is not None:
        # Process the record

        urls = []
        for product in products:
            if "id" not in product:
                continue
            urls.append("https://tiki.vn/api/v2/products/" + str(product["id"]))

        print(urls)

        process.crawl(TikiproductapiSpider, start_urls=urls)
        process.start()

        products = collection.find(query).limit(2)

        test = test + 1
        if test == 1:
            products = None


    if(database is not None and mongodb is not None): 
        database.close(mongodb)