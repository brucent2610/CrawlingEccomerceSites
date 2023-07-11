import os
import sys

from csv import writer

from time import sleep
from datetime import datetime

from Database import MongoDB

print("Running", os.getenv("ENV"))

database = MongoDB()
mongodb = database.initialize()

LIMIT = 2000
RUNNING = 6

def get_ingredients(item):
    specifications = item["specifications"]
    for specification in specifications:
        if "attributes" not in specification:
            continue
        attributes = specification["attributes"]

        for attribute in attributes:
            if "code" not in attribute:
                continue
            if "value" not in attribute:
                continue
            code = attribute["code"]
            if code != "ingredients":
                continue
            return attribute["value"]

    return ""
            

if __name__ == "__main__": 

    collection = mongodb["products"]
    query = {"specifications.attributes.code": "ingredients", "is_ingredients": {"$ne": int(RUNNING)}}
    
    products = collection.find(query).limit(int(LIMIT))

    path = '/usr/src/csv/ingredients.csv'

    isExist = False
    if os.path.exists(path):
        isExist = True

    with open(path, 'a') as f_object:

        # Pass this file object to csv.writer()
        # and get a writer object
        writer_object = writer(f_object)

        if isExist != True:
            writer_object.writerow([
                "product_id",
                "ingredients"
            ])

        run_no = 0

        while products:
            ids = []
            for item in products:

                if "id" not in item:
                    continue

                if "error" in item and item["error"] != False:
                    continue

                if "specifications" not in item:
                    continue

                ingredients = get_ingredients(item)

                print("ingredients", ingredients)

                writer_object.writerow([
                    item["id"],
                    ingredients
                ])
                ids.append(item["id"])

            if len(ids) <= 0:
                break

            result = collection.update_many({
                'id': {
                    "$in": ids
                }
            }, {
                '$set': {
                    "is_ingredients": int(RUNNING)
                }
            })
            print("Result", result.modified_count)

            run_no = run_no + 1
            print("Run", str(run_no), " times")

            products = collection.find(query).limit(int(LIMIT))

        if database is not None and mongodb is not None: 
            database.close(mongodb)

        # Close the file object
        f_object.close()

    sys.exit()