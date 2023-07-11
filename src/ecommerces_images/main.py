import os
import sys

from time import sleep
from datetime import datetime

from Database import MongoDB

from utils import store_images_2

print("Running", os.getenv("ENV"))

database = MongoDB()
mongodb = database.initialize()

LIMIT = 100

def get_categories(category_ids, result):
    collection = mongodb["categories"]
    query = {
        "parent_id": {
            "$in": category_ids
        }
    }
    categories = collection.find(query)

    category_ids = []
    for category in categories:
        result.append(category["category_id"])
        category_ids.append(category["category_id"])

    if len(category_ids) <= 0:
        return result
    
    return get_categories(category_ids, result)

if __name__ == "__main__": 

    category_ids = get_categories([931,915], [])

    collection = mongodb["products"]
    query = {
        "categories.id": {
            "$in": category_ids
        },
        "progress_image_status": {
            "$ne": 1
        }
    }
    products = collection.find(query).limit(int(LIMIT))

    run_no = 0
    while products is not None:
        ids = []
        for product in products:
            if "id" not in product:
                continue
            if "images" not in product:
                continue
            store_images_2(product["id"], product["images"])
            if "base_url" in product:
                store_images_2(product["id"], product["base_url"])
            ids.append(product["id"])
            
        result = collection.update_many({
            'id': {
                "$in": ids
            }
        }, {
            '$set': {
                "progress_image_status": 1
            }
        })

        run_no = run_no + 1
        print("Result Images", result.modified_count)
        print("Run", str(run_no), " times")

        products = collection.find(query).limit(int(LIMIT))

    if database is not None and mongodb is not None: 
        database.close(mongodb)