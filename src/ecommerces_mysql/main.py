import os
import sys

from time import sleep
from datetime import datetime

from Database import MongoDB, MySQLDB

from utils import store_mysql_skip_insert, store_many_mysql

print("Running", os.getenv("ENV"))

database = MongoDB()
mongodb = database.initialize()
mysqldb = MySQLDB()

LIMIT = 200
SKIP = os.getenv("SKIP")

if __name__ == "__main__": 

    collection = mongodb["products"]
    query = {
        "progress_mysql_status": {
            "$ne": 1
        }
    }
    
    products = collection.find(query).skip(int(SKIP)).limit(int(LIMIT))

    run_no = 0
    while products:
        ids = []
        insert_products = []
        for item in products:

            if "id" not in item:
                continue

            if "error" in item and item["error"] != False:
                continue

            try:
                selling_count = 0
                if "quantity_sold" in item:
                    quantity_sold = item["quantity_sold"]
                    selling_count = quantity_sold["value"] if quantity_sold is not None and 'value' in quantity_sold else 0

                category_id = 0
                if "categories" in item:
                    categories = item["categories"]
                    category_id = categories['id'] if categories is not None and 'id' in categories else 0

                is_insert = store_mysql_skip_insert(mysqldb, {
                    "name": item["name"] if 'name' in item else "",
                    "short_description": item["short_description"] if 'short_description' in item else "",
                    "description": item["description"] if 'description' in item else "",
                    "url_key": item["url_key"] if 'url_key' in item else "",
                    "rating_average": item["rating_average"] if 'rating_average' in item else 0,
                    "selling_count": selling_count,
                    "price": item["price"] if 'price' in item else 0,
                    "category_id": category_id,
                    "id": item["id"],
                    "day_ago_created": item["day_ago_created"] if 'day_ago_created' in item else 0
                })

                if(is_insert):
                    insert_products.append([
                        item["id"],
                        item["name"] if 'name' in item else "",
                        item["short_description"] if 'short_description' in item else "",
                        item["description"] if 'description' in item else "",
                        item["url_key"] if 'url_key' in item else "",
                        item["rating_average"] if 'rating_average' in item else 0,
                        selling_count,
                        item["price"] if 'price' in item else 0,
                        category_id,
                        item["day_ago_created"] if 'day_ago_created' in item else 0
                    ])
                else:
                    ids.append(item["id"])

            except Exception as error:
                print(error)

        try:
            store_many_mysql(mysqldb, insert_products)

            for insert_product in insert_products:
                ids.append(insert_product[0])

        except Exception as error:
            print(error)

        result = collection.update_many({
            'id': {
                "$in": ids
            }
        }, {
            '$set': {
                "progress_mysql_status": 1
            }
        })

        run_no = run_no + 1
        print("Result", result.modified_count)
        print("Run", str(run_no), " times")

        products = collection.find(query).skip(int(SKIP)).limit(int(LIMIT))

    if database is not None and mongodb is not None: 
        database.close(mongodb)
    if database is not None and mysqldb is not None:
        mysqldb.close()

    sys.exit()