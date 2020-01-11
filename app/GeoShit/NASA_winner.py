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

from app import ee

def modis_ndvi_time(geom):
    modis_collection = ee.ImageCollection("MODIS/006/MOD13Q1").filter(ee.Filter.date('2018-01-01', '2019-01-01')).filterBounds(geom)
    modis_ndvi = modis_collection.select('NDVI')

    reference_modis = modis_ndvi.first().clip(geom)
    latlon_ref = ee.Image.pixelLonLat().addBands(reference_modis)
    latlon_ref = latlon_ref.reduceRegion(reducer=ee.Reducer.toList(), geometry=geom, maxPixels=1e9, scale=250)

    reference_length = ee.Number(ee.List(latlon_ref.get("latitude")).length()).getInfo()

    lats = (np.array((ee.Array(latlon_ref.get("latitude")).getInfo()))).tolist()
    lons = (np.array((ee.Array(latlon_ref.get("longitude")).getInfo()))).tolist()

    def time_series(img, serie_list):

        img = img.clip(geom)
        latlon = ee.Image.pixelLonLat().addBands(img)
        element = latlon.reduceRegion(reducer=ee.Reducer.toList(), geometry=geom, maxPixels=1e8, scale=250).get('NDVI')
        pixel_length = ee.List(element).length()
        add = ee.List(serie_list).add(element)
        not_add = ee.List(serie_list)

        return ee.Algorithms.If(pixel_length.eq(reference_length), add, not_add)

    def dates_series(img, serie_list):

        img = img.clip(geom)
        latlon = ee.Image.pixelLonLat().addBands(img)
        element = latlon.reduceRegion(reducer=ee.Reducer.toList(), geometry=geom, maxPixels=1e8, scale=250).get('NDVI')
        pixel_length = ee.List(element).length()
        date = ee.Date(img.get('system:time_start')).format()
        add = ee.List(serie_list).add(date)
        not_add = ee.List(serie_list)

        return ee.Algorithms.If(pixel_length.eq(reference_length), add, not_add)

    ndvi_series_list  = ee.List(modis_ndvi.iterate(time_series, ee.List([])))
    dates_series_list = ee.List(modis_ndvi.iterate(dates_series, ee.List([])))

    ndvi  = np.array(ee.Array(ndvi_series_list).getInfo()) / 10000
    dates = ee.List(dates_series_list).getInfo()
    serie_dates =[]

    for d in dates:
        serie_dates.append(d[:10])

    max_lats, min_lats, max_lons, min_lons, nrows, ncols = coordinates_parameters(lats, lons)
    n_images = ndvi.shape[0]

    ndvi_data = np.zeros((ncols, nrows, n_images))
    ys = abs(max_lats-min_lats)/nrows
    xs = abs(max_lons-min_lons)/ncols

    parameters = [min_lons, xs, 0, max_lats, 0, -ys]

    for n in range(0, n_images):
        for i in range(0, reference_length):
            try:
                col,row = world2Pixel(parameters, lons[i], lats[i])
                ndvi_data[int(col)-1][int(row)-1][n] = ndvi[n][i]
            except:
                print("Error en pixel! ")

    return serie_dates, ndvi_data, parameters

def ndvi_sentinel_calculation(geom, past_time, date_time):

    def ndvi_filter(image):
        ndvi = image.clip(geom).normalizedDifference(['B8', 'B4'])
        return ndvi

    sentinel_collection = ee.ImageCollection("COPERNICUS/S2_SR").filter(ee.Filter.date(past_time, date_time)).filterBounds(geom)
    sentinel_collection_now = sentinel_collection.sort('system:time_start', False).limit(3)

    ndvi_collection_now = sentinel_collection_now.map(ndvi_filter)

    now_date = ee.Date(sentinel_collection_now.first().get('system:time_start')).format().getInfo()

    ndvi_median_now = ndvi_collection_now.reduce(ee.Reducer.max())
    latlon_now = ee.Image.pixelLonLat().addBands(ndvi_median_now)
    latlon_now = latlon_now.reduceRegion(reducer=ee.Reducer.toList(), geometry=geom, maxPixels=1e9, scale=10);

    data_now = np.array((ee.Array(latlon_now.get("nd_max")).getInfo()))
    lats = np.array((ee.Array(latlon_now.get("latitude")).getInfo()))
    lons = np.array((ee.Array(latlon_now.get("longitude")).getInfo()))

    max_lats, min_lats, max_lons, min_lons, nrows, ncols = coordinates_parameters(lats, lons)
    coords = [(max_lats, min_lons), (min_lats,max_lons)]
    ndata = len(data_now)

    ndvi_data_now = np.full((ncols, nrows), np.nan)

    ys = abs(max_lats-min_lats)/nrows
    xs = abs(max_lons-min_lons)/ncols

    parameters = [min_lons, xs, 0, max_lats, 0, -ys]

    for i in range(0, ndata):
        col,row = world2Pixel(parameters, lons[i], lats[i])
        ndvi_data_now[int(col)-1][int(row)-1] = data_now[i]

    area = len(data_now)
    stats = {}
    stats['mean'] = np.mean(data_now)
    stats['std']  = np.std(data_now)
    stats['mean/pixel'] = np.mean(data_now)/area
    stats['p_0.05'] = np.percentile(data_now, 5)
    stats['p_0.25'] = np.percentile(data_now, 25)
    stats['p_0.50'] = np.percentile(data_now, 50)
    stats['p_0.75'] = np.percentile(data_now, 75)
    stats['p_0.95'] = np.percentile(data_now, 95)
    stats['area_0.00'] = len(data_now[data_now<0.05])/area
    stats['area_0.25'] = len(data_now[(data_now>=0.05) & (data_now<0.25)])/area
    stats['area_0.50'] = len(data_now[(data_now>=0.25) & (data_now<0.5)])/area
    stats['area_0.75'] = len(data_now[(data_now>=0.5) & (data_now<0.75)])/area
    stats['area_1.00'] = len(data_now[data_now>=0.75])/area
    stats['area'] = 100*area

    return ndvi_data_now, now_date, coords, parameters, stats

def geom_loading( polygon_dictionary ):

    polygon_dictionary = polygon_dictionary['features'][0]['geometry']
    geom_type = polygon_dictionary["type"]

    if geom_type == 'Polygon':
        geom = ee.Geometry.Polygon(polygon_dictionary["coordinates"])
    else:
        geom = ee.Geometry.MultiPolygon(polygon_dictionary["coordinates"])

    x = geom.centroid().getInfo()['coordinates'][0]
    y = geom.centroid().getInfo()['coordinates'][1]

    return geom, x, y

def world2Pixel(geoMatrix, x, y):
    ulX   = geoMatrix[0]
    ulY   = geoMatrix[3]
    xDist = geoMatrix[1]
    yDist = -geoMatrix[5]
    pixel = int((x - ulX) / xDist)
    line  = int((ulY - y) / yDist)
    return (pixel, line)

def coordinates_parameters(lats, lons):

    unique_lats = np.unique(lats)
    unique_lons = np.unique(lons)
    max_lats = np.max(unique_lats)
    min_lats = np.min(unique_lats)
    max_lons = np.max(unique_lons)
    min_lons = np.min(unique_lons)
    ncols    = len(unique_lons)
    nrows    = len(unique_lats)

    return max_lats, min_lats, max_lons, min_lons, nrows, ncols

def colormap_image(file_name, image):

    image = np.flipud( image )
    image = np.rot90( image, 3 )

    cm_hot = plt.get_cmap('hot')
    image_a = np.full(image.shape, 0)
    image_a[np.isfinite(image)] = 255
    image_a = np.uint8(image_a)

    image[np.where(image==np.nan)] = 0
    image[np.where(image<0)] = 0

    image_rgba = cm_hot(image)
    image_rgba = np.uint8(image_rgba * 255)

    image_r, image_g, image_b = image_rgba[:,:,0], image_rgba[:,:,1], image_rgba[:,:,2]

    image_rgba = np.stack([image_r, image_g, image_b, image_a], axis=2)
    image = Image.fromarray(image_rgba)

    image.save(file_name  + '.png')

def upload_timeserie(timeserie):
    np.save('time_serie.npy', timeserie)
    blob = bucket.blob('time_serie.npy')
    blob.upload_from_filename('time_serie.npy')
    blob.make_public()
    os.remove('time_serie.npy')
    url = blob.public_url
    return url

def upload_ndvi( file_name, bucket ):

    blob = bucket.blob(file_name + '.png')
    blob.upload_from_filename(file_name + '.png')
    blob.make_public()
    os.remove(file_name + '.png')
    return blob.public_url

def upload_polygon(geometry_file):

    df = gpd.read_file(geometry_file)
    df = df['geometry'].to_crs(epsg=4326)
    geom_file = df.to_json()
    geom_file = json.loads(geom_file)
    geom_file = geom_file['features'][0]['geometry']
    return geom_file

file_json = 'TestJS-9381bfacfaba.json'
