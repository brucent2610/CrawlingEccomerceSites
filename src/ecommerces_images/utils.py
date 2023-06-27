import os

import requests
import mimetypes

from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath

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

def store_images(domain, urls):
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

        # Write the content, which is binary, to the file which is also opened
        # in binary mode.
        with open(file_name, "wb") as f_imag:
            f_imag.write(response.content)

