import os

import requests
import mimetypes

from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath

from Database import MySQLDB

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

def store_images_2(product_id, images):
    urls = []

    image_index = 0
    for image in images:
        if type(image) == str:
            urls.append(image)
            continue
        if image_index >= 5:
            break
        if "base_url" in image:
            urls.append(image["base_url"])
        image_index = image_index + 1

    index = 1
    for url in urls:
        try:
            response = requests.get(url)

            # Get the extension of the image from content type.
            content_type = response.headers["Content-Type"]
            # Can guess common image types, such as jpeg, png, tiff, etc.
            img_ext = mimetypes.guess_extension(content_type)

            path = "../images/tiki/" + str(product_id)
            
            name = str(product_id) + "_" + str(index) + img_ext

            if not os.path.exists(path):
                os.makedirs(path)

            file_name = path + "/" + name

            if os.path.isfile(file_name):
                print(file_name + " exists")
                return

            # Write the content, which is binary, to the file which is also opened
            # in binary mode.
            with open(file_name, "wb") as f_imag:
                f_imag.write(response.content)

                print("Store "+ file_name + " success")
                
        except Exception as error:
            print('Could not store image: ', error) 
        finally:
            index = index + 1

