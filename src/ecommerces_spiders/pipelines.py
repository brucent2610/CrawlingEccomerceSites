# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from Database import Database

class EcommercesSpidersPipeline:

    def __init__(self):
        self.database = Database()
        self.mongodb = self.database.initialize()

    def process_item(self, item, spider):

        if spider.name == "TikiCategoryApi":
            ecommercesSpidersTikiCategoryPipeline = EcommercesSpidersTikiCategoryPipeline(self.mongodb)
            return ecommercesSpidersTikiCategoryPipeline.process_item(item, spider)
        
        if spider.name == "TikiProductApi":
            ecommercesSpidersTikiProductPipeline = EcommercesSpidersTikiProductPipeline(self.mongodb)
            return ecommercesSpidersTikiProductPipeline.process_item(item, spider)

        if spider.name == "TikiPage":
            ecommercesSpidersTikiPagePipeline = EcommercesSpidersTikiPagePipeline(self.mongodb)
            return ecommercesSpidersTikiPagePipeline.process_item(item, spider)

        if spider.name == "TikiCategoriesPage":
            ecommercesSpidersTikiPagePipeline = EcommercesSpidersTikiPagePipeline(self.mongodb)
            return ecommercesSpidersTikiPagePipeline.process_item(item, spider)

        return item

    def close_spider(self, spider):
        if(self.database is not None and self.mongodb is not None): 
            self.database.close(self.mongodb)

class EcommercesSpidersTikiPagePipeline:

    TAG = "TikiPagePipeline"

    def __init__(self, mongodb):
        self.mongodb = mongodb

    def process_item(self, item, spider):

        print(self.TAG, "Start Pipeline: ", spider.name)

        try:
            collection = self.mongodb["categories"] 

            if 'main_category_id' in item and 'paging' in item:
                main_category = collection.find_one({
                    'category_id': item["main_category_id"]
                })
                if(main_category):
                    try:
                        main_category_updated = main_category.copy()
                        paging = item["paging"]
                        main_category_updated['current_page'] = paging["current_page"]
                        main_category_updated['from'] = paging["from"]
                        main_category_updated['last_page'] = paging["last_page"]
                        main_category_updated['per_page'] = paging["per_page"]
                        main_category_updated['to'] = paging["to"]
                        main_category_updated['total'] = paging["total"]

                        main_category_updated['has_sub'] = True
                        if("categories" not in item and len(item["categories"]) <= 0):
                            main_category_updated['has_sub'] = False
                        
                        collection.update_one(
                            {'_id': main_category["_id"]}, 
                            {'$set': main_category_updated}
                        )
                    except Exception as error:
                        print(self.TAG, 'Could not store Main Category: ', error) 


            
            if("categories" not in item and len(item["categories"]) <= 0):
                print(self.TAG, "No Categories")
                return item

            categories = item['categories']
            inserted_categories = []

            for cat in categories:
                if('category_id' not in cat):
                    continue

                category = collection.find_one({
                    'category_id': cat["category_id"]
                })
                if(category):
                    category_updated = cat.copy()
                    del category_updated['category_id']
                    result = collection.update_one({
                        'category_id': cat["category_id"]
                    }, {
                        '$set': category_updated
                    })
                    print(self.TAG, 'No. Updated record: ', result.modified_count)
                    print(self.TAG, 'Success update one category: ', cat["category_id"])
                else:
                    inserted_categories.append(cat)

            if(len(inserted_categories) > 0):
                result = collection.insert_many(inserted_categories)
                print(self.TAG, 'No. Inserted _Ids: ', str(len(result.inserted_ids)))
                print(self.TAG, 'Success insert categores', [inserted_category['category_id'] for inserted_category in inserted_categories])

        except Exception as error:
            print(self.TAG, 'Could not store category: ', error) 
        finally:
            return item

class EcommercesSpidersTikiCategoryPipeline:

    TAG = "TikiCategoryPipeline"

    def __init__(self, mongodb):
        self.mongodb = mongodb

    def process_item(self, item, spider):

        print(self.TAG, "Start Pipeline: ", spider.name)

        if "categories" in item:
            ecommercesSpidersTikiPagePipeline = EcommercesSpidersTikiPagePipeline(self.mongodb)
            ecommercesSpidersTikiPagePipeline.process_item(item, spider)


        if("products" not in item and len(item["products"]) <= 0):
            print(self.TAG, "No Products")
            return item
        
        try:
            collection = self.mongodb["products"] 

            products = item['products']
            inserted_products = []

            category_id = []
            if 'main_category_id' in item:
                category_id = int(item["main_category_id"])

            for pro in products:
                if('id' not in pro):
                    continue
                
                product = collection.find_one({
                    'id': pro["id"]
                })
                if(product):
                    product_updated = pro.copy()
                    del product_updated['id']
                    if "category_ids" in product:
                        product["category_ids"].append(category_id)
                    result = collection.update_one({
                        'id': pro["id"]
                    }, {
                        '$set': product_updated
                    })
                    print(self.TAG, 'No. Updated record: ', result.modified_count)
                    print(self.TAG, 'Success update one product: ', pro["id"])
                else:
                    pro["category_ids"] = [category_id]
                    inserted_products.append(pro)

            if(len(inserted_products) > 0):
                result = collection.insert_many(inserted_products)
                print(self.TAG, 'No. Inserted _Ids: ', str(len(result.inserted_ids)))
                print(self.TAG, 'Success insert products', [inserted_product['id'] for inserted_product in inserted_products])

        except Exception as error:
            print(self.TAG, 'Could not store product: ', error) 
        finally:
            return item

class EcommercesSpidersTikiProductPipeline:

    TAG = "TikiProductPipeline"

    def __init__(self, mongodb):
        self.mongodb = mongodb

    def process_item(self, item, spider):
        if(item["id"] is None):
            print(self.TAG, "No exist product id")
            return item
        try:
            print(self.TAG, "Start Pipeline: ", spider.name)

            collection = self.mongodb["products"] 
            product = collection.find_one({
                'id': item["id"]
            })
            if product:
                item_updated = item.copy()
                del item_updated['id']
                result = collection.update_one({
                    'id': item["id"]
                }, {
                    '$set': item_updated
                })
                print(self.TAG, 'No. Updated record: ',result.modified_count)
                print(self.TAG, 'Success update one product: ', item["id"])
            else:
                result = collection.insert_one(item)

                print(self.TAG, 'Inserted _Id: ', result.inserted_id)
                print(self.TAG, 'Success insert one product: ', item["id"])

        except Exception as error:
            print(self.TAG, 'Could not store product: ', error) 
        finally:
            return item

