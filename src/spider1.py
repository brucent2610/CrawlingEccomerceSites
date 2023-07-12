#Run init the main categories in homepage

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

    process.start()

    if(database is not None and mongodb is not None): 
        database.close(mongodb)

    sys.exit()