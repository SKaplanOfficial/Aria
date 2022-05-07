"""
Various utilities for Aria

These utilities fall outside the bounds of existing Manager classes.
New managers should be made, over time, that incorporate these utilities.

Last Updated: Version 0.0.2
"""

import random
import json
import urllib.request
import math
from PIL import Image

def rselect(list):
    """ Selects and returns a random element in a list if there are any elements in the list. Otherwise, returns None. """
    if len(list) > 0:
        return random.choice(list)
    return None

def get_json(query_url, storage_obj=None):
    """ Makes a JSON request. """
    if storage_obj != None:
        if query_url == storage_obj.last_query:
            return storage_obj.last_response

    response = urllib.request.urlopen(query_url)
    response_json = json.loads(response.read())

    if storage_obj != None:
        storage_obj.last_query = query_url
        storage_obj.last_response = response_json

    return response_json

def mosaic(images, base_dim):
    """ Creates an NxN mosaic of the supplied list of images where each image is rescaled to the supplied base dimensions. """
    root = math.sqrt(len(images))
    while not root.is_integer():
        images.pop()
        root = math.sqrt(len(images))

    root = int(root)
    dim = (root * base_dim[0], root * base_dim[1])
    new_image = Image.new("RGB", dim)

    for r in range(0, root):
        for c in range(0, root):
            dest = images[r+c*root]["url"]
            path, HTTPMessage = urllib.request.urlretrieve(dest)
            img = Image.open(path)
            width = int(max(base_dim[1], base_dim[0]/img.size[0] * img.size[1]))
            img = img.resize((base_dim[0], width), Image.ANTIALIAS)
            new_image.paste(img, (base_dim[0]*c, base_dim[1]*r))
    return new_image