import os

import requests
import mimetypes

from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath

from Database import MySQLDB

def is_exist(product_id, index):

    path = "../images/tiki/" + str(product_id)
    
    name = str(product_id) + "_" + str(index) + ".jpg"

    file_name = path + "/" + name

    if os.path.isfile(file_name):
        print(file_name + " exists")
        return True

    return False

def get_path(value):
    if(value == None):
        return None
    paths = PurePosixPath(unquote(urlparse(value).path)).parts
    l_element = len(paths)-1
    
    return '/'.join(paths[:l_element])

def get_name(value):
    if(value == None):
        return None
    paths = PurePosixPath(unquote(urlparse(value).path)).parts
    return (paths[-1])

def store_many_mysql(mysqldb, items):
    if len(items) <= 0:
        return
    query = """INSERT INTO products (product_id, name, short_description, description, url, rating, selling_count, price, category_id, day_ago_created) VALUES """ + """,""".join("(%s, %s, %s, %s, %s ,%s, %s, %s, %s, %s)""" for _ in items)
    flattened_values = [item for sublist in items for item in sublist]

    print(query)
    print(flattened_values)

    mysqldb.commit(query, flattened_values)

    print("products inserted.", str(len(items)))

def store_mysql_skip_insert(mysqldb, item):

    product_mysql = mysqldb.fetchone("select product_id from products where product_id = %s", (item['id'],))

    if product_mysql:
        mysqldb.commit(""" 
            UPDATE products
                SET name = %s,
                    short_description = %s,
                    description = %s,
                    url = %s,
                    rating = %s,
                    selling_count = %s,
                    price = %s,
                    category_id = %s,
                    day_ago_created = %s
                WHERE product_id = %s;""", (
                item["name"] if 'name' in item else "",
                item["short_description"] if 'short_description' in item else "",
                item["description"] if 'description' in item else "",
                item["url_key"] if 'url_key' in item else "",
                item["rating_average"] if 'rating_average' in item else 0,
                item["selling_count"] if 'selling_count' in item else 0,
                item["price"] if 'price' in item else 0,
                item["category_id"] if 'category_id' in item else 0,
                item["day_ago_created"] if 'day_ago_created' in item else 0,
                item["id"],
            ))

        print("Updated MySQL: ", item["id"])
        return False
    else:
        return True

def store_mysql(mysqldb, item):
    # print("store_mysql", item)
    product_mysql = mysqldb.fetchone("select product_id from products where product_id = %s", (item['id'],))

    if product_mysql:
        mysqldb.commit(""" 
            UPDATE products
                SET name = %s,
                    short_description = %s,
                    description = %s,
                    short_url = %s,
                    rating_average = %s,
                    selling_count = %s,
                    price = %s,
                    category_id = %s
                WHERE product_id = %s;""", (
                item["name"] if 'name' in item else "",
                item["short_description"] if 'short_description' in item else "",
                item["description"] if 'description' in item else "",
                item["short_url"] if 'short_url' in item else "",
                item["rating_average"] if 'rating_average' in item else 0,
                item["selling_count"] if 'selling_count' in item else 0,
                item["price"] if 'price' in item else 0,
                item["category_id"] if 'category_id' in item else 0,
                item["id"],
            ))
        print("Updated MySQL: ", item["id"])
    else:
        mysqldb.commit(""" INSERT INTO products (
            product_id, 
            name, 
            short_description, 
            description, 
            short_url, 
            rating_average, 
            selling_count, 
            price, 
            category_id) VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s)""", (
            item["id"],
            item["name"] if 'name' in item else "",
            item["short_description"] if 'short_description' in item else "",
            item["description"] if 'description' in item else "",
            item["short_url"] if 'short_url' in item else "",
            item["rating_average"] if 'rating_average' in item else 0,
            item["selling_count"] if 'selling_count' in item else 0,
            item["price"] if 'price' in item else 0,
            item["category_id"] if 'category_id' in item else 0
        ))
        print("Stored MySQL: ", item["id"])

def store_images(domain, images):
    urls = []

    for image in images:
        if type(image) == str:
            urls.append(image)
            continue
        if "base_url" in image:
            urls.append(image["base_url"])
        if "large_url" in image:
            urls.append(image["large_url"])
        if "medium_url" in image:
            urls.append(image["medium_url"])
        if "small_url" in image:
            urls.append(image["small_url"])
        if "thumbnail_url" in image:
            urls.append(image["thumbnail_url"])

    for url in urls:
        
        response = requests.get(url)

        # Get the extension of the image from content type.
        content_type = response.headers["Content-Type"]
        # Can guess common image types, such as jpeg, png, tiff, etc.
        img_ext = mimetypes.guess_extension(content_type)

        path = "../images/"+domain+"/"+ get_path(url)
        name = get_name(url)

        if not os.path.exists(path):
            os.makedirs(path)

        # Construct the image name.
        file_name = path + "/" + name + img_ext

        if os.path.isfile(file_name):
            print(file_name + " exists")
            return

        # Write the content, which is binary, to the file which is also opened
        # in binary mode.
        with open(file_name, "wb") as f_imag:
            f_imag.write(response.content)

            print("Store "+ file_name + " success")

