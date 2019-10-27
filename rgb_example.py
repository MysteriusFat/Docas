import os
from datetime import datetime, timedelta
import ee
from google.cloud import bigquery, storage
import json
import numpy as np
import pandas as pd
import geopandas as gpd
import fiona
from PIL import Image
import matplotlib.pyplot as plt
from NASA_winner import *

def rgb_sentinel(geom, past_time, date_time):

    def rgb_filter(image):
        rgb = image.clip( geom ).select( ['TCI_R','TCI_G','TCI_B'] )
        return rgb

    sentinel_collection = ee.ImageCollection("COPERNICUS/S2_SR").filter(ee.Filter.date(past_time, date_time)).filterBounds(geom)
    sentinel_collection_now = sentinel_collection.sort('system:time_start', False).limit(3)

    ndvi_collection_now = sentinel_collection_now.map(rgb_filter)

    now_date = ee.Date(sentinel_collection_now.first().get('system:time_start')).format().getInfo()

    ndvi_median_now = ndvi_collection_now.reduce(ee.Reducer.median())
    latlon_now = ee.Image.pixelLonLat().addBands(ndvi_median_now)
    latlon_now = latlon_now.reduceRegion(reducer=ee.Reducer.toList(), geometry=geom, maxPixels=1e8, scale=10);

    r = np.array((ee.Array(latlon_now.get("TCI_R_median")).getInfo()))
    g = np.array((ee.Array(latlon_now.get("TCI_G_median")).getInfo()))
    b = np.array((ee.Array(latlon_now.get("TCI_B_median")).getInfo()))

    lats = np.array((ee.Array(latlon_now.get("latitude")).getInfo()))
    lons = np.array((ee.Array(latlon_now.get("longitude")).getInfo()))

    max_lats, min_lats, max_lons, min_lons, nrows, ncols = coordinates_parameters(lats, lons)
    coords = [(max_lats, min_lons), (min_lats,max_lons)]
    ndata = len(r)

    rgb_data = np.full((ncols, nrows, 3), np.nan)

    ys = abs(max_lats-min_lats)/nrows
    xs = abs(max_lons-min_lons)/ncols

    parameters = [min_lons, xs, 0, max_lats, 0, -ys]

    for i in range(0, ndata):
        col,row = world2Pixel(parameters, lons[i], lats[i])
        rgb_data[int(col)-1][int(row)-1][0] = r[i]
        rgb_data[int(col)-1][int(row)-1][1] = g[i]
        rgb_data[int(col)-1][int(row)-1][2] = b[i]

    return rgb_data, now_date, coords, parameters

def colormap_rgb(file_name, image):

    image = np.flipud( image )
    image = np.rot90( image, 3 )

    image_a = np.full((image.shape[0],image.shape[1]), 0)
    image_a[np.isfinite(np.sum(image, axis=2))] = 255
    image_a = np.uint8(image_a)

    image[np.where(image==np.nan)] = 0

    image_rgb = np.uint8(image)

    image_r, image_g, image_b = image_rgb[:,:,0], image_rgb[:,:,1], image_rgb[:,:,2]

    image_rgba = np.stack([image_r, image_g, image_b, image_a], axis=2)
    image = Image.fromarray(image_rgba)
    image.save(file_name + '.png')
