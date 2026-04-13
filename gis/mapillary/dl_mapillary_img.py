#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : ccv 
@File    : dl_mapillary_img.py
@Site    : 
@Author  : Gavin Gao
@Date    : 7/23/22 6:44 PM
@Ref     : https://blog.mapillary.com/update/2021/06/23/getting-started-with-the-new-mapillary-api-v4.html
@Depend  :
    pip install mapbox-vector-tile
    pip install mercantile
    pip install vt2geojson
    pip install request
    pip install requests
    pip install protobuf==3.20
"""

import os
import requests
import json
import mercantile
import mapbox_vector_tile
from vt2geojson.tools import vt_bytes_to_geojson

# define an empty geojson as output
output = {"type": "FeatureCollection", "features": []}

# vector tile endpoints -- change this in the API request to reference the correct endpoint
tile_coverage = 'mly1_public'

# tile layer depends which vector tile endpoints:
# 1. if map features or traffic signs, it will be "point" always
# 2. if looking for coverage, it will be "image" for points, "sequence" for lines, or "overview" for far zoom
tile_layer = "image"

# Mapillary access token -- user should provide their own
# https://www.mapillary.com/dashboard/developers --> Client Token
access_token = 'MLY|5265533410228693|510618f35206947fb7689bdcf03a0bae'  # 'MLY|XXX'

# a bounding box in [east_lng,_south_lat,west_lng,north_lat] format
# west, south, east, north = [-80.13423442840576, 25.77376933762778, -80.1264238357544, 25.788608487732198]
west, south, east, north = [-77.0375, 38.8967, -77.0355, 38.8987]  # whitehouse

# get the list of tiles with x and y coordinates which intersect our bounding box
# MUST be at zoom level 14 where the data is available, other zooms currently not supported
tiles = list(mercantile.tiles(west, south, east, north, 14))

# loop through list of tiles to get tile z/x/y to plug in to Mapillary endpoints and make request
for tile in tiles:
    tile_url = 'https://tiles.mapillary.com/maps/vtp/{}/2/{}/{}/{}?access_token={}'.format(tile_coverage, tile.z,
                                                                                           tile.x, tile.y, access_token)
    response = requests.get(tile_url)
    data = vt_bytes_to_geojson(response.content, tile.x, tile.y, tile.z, layer=tile_layer)

    # push to output geojson object if yes
    for feature in data['features']:
        output['features'].append(feature)

        # get lng,lat of each feature
        lng = feature['geometry']['coordinates'][0]
        lat = feature['geometry']['coordinates'][1]

        # ensure feature falls inside bounding box since tiles can extend beyond
        if west < lng < east and south < lat < north:

            # create a folder for each unique sequence ID to group images by sequence
            sequence_id = feature['properties']['sequence_id']
            if not os.path.exists(sequence_id):
                os.makedirs(sequence_id)

            # request the URL of each image
            field_thumb = 'thumb_1024_url'
            image_id = feature['properties']['id']
            header = {'Authorization': 'OAuth {}'.format(access_token)}
            url = 'https://graph.mapillary.com/{}?fields={}'.format(image_id, field_thumb)
            r = requests.get(url, headers=header)
            data = r.json()
            image_url = data[field_thumb]

            # save each image with ID as filename to directory by sequence ID
            with open('{}/{}.jpg'.format(sequence_id, image_id), 'wb') as handler:
                image_data = requests.get(image_url, stream=True).content
                handler.write(image_data)

# save a local geojson with the filtered data
with open('images.geojson', 'w') as f:
    json.dump(output, f)
