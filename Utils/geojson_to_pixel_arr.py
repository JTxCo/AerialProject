#!/usr/bin/env python2
# -*- coding: utf-8 -*-


'''
This is script fround at: https://medium.com/the-downlinq/getting-started-with-spacenet-data-827fd2ec9f53

This utilizes the spacenet utilites from: https://github.com/SpaceNetChallenge/utilities/tree/master

'''



from osgeo import gdal, osr, ogr, gdal

import numpy as np
import json
import sys
import os

####################
# download spacenet utilities from:
#  https://github.com/SpaceNetChallenge/utilities/tree/master/python/spaceNet 
# path_to_spacenet_utils = '/path/to/spacenet/utils/'
# sys.path.extend([path_to_spacenet_utils])
# from spaceNet import geoTools as gT



# 1) Compute the real path to your utilities repo
#    Adjust this so it matches where you cloned the GitHub utilities
#    e.g. "~/AerialProject/Utils/utilities/spacenetutilities"
BASE_DIR = os.path.dirname(__file__)                                # .../AerialProject/Utils
SPACENET_UTILS_DIR = os.path.join(
    BASE_DIR,
    "utilities",            # the folder you showed under Utils/
    "spacenetutilities"     # the cloned SpaceNetUtilities/python/spaceNet folder
)
SPACENET_UTILS_DIR = os.path.expanduser(SPACENET_UTILS_DIR)
assert os.path.isdir(SPACENET_UTILS_DIR), f"Cannot find: {SPACENET_UTILS_DIR}"

# 2) Add that folder to Python’s import search path
sys.path.insert(0, SPACENET_UTILS_DIR)

# 3) Now you can import geoTools
import geoTools as gT

###############################################################################    
def latlon2pixel(lat, lon, input_raster='', targetsr='', geom_transform=''):
    '''
        Function was removed from geoTools after the Medium article was initially publishd so this function is based on the old version
        Make sure to use this updated version not the old one in the article. 
        type: (object, object, object, object, object) -> object
    '''
    sourcesr = osr.SpatialReference()
    sourcesr.ImportFromEPSG(4326)

    geom = ogr.Geometry(ogr.wkbPoint)
    geom.AddPoint(lon, lat)

    if targetsr == '':
        src_raster = gdal.Open(input_raster)
        targetsr = osr.SpatialReference()
        targetsr.ImportFromWkt(src_raster.GetProjectionRef())
    coord_trans = osr.CoordinateTransformation(sourcesr, targetsr)
    if geom_transform == '':
        src_raster = gdal.Open(input_raster)
        transform = src_raster.GetGeoTransform()
    else:
        transform = geom_transform

    x_origin = transform[0]
    # print(x_origin)
    y_origin = transform[3]
    # print(y_origin)
    pixel_width = transform[1]
    # print(pixel_width)
    pixel_height = transform[5]
    # print(pixel_height)
    geom.Transform(coord_trans)
    # print(geom.GetPoint())
    x_pix = (geom.GetPoint()[0] - x_origin) / pixel_width
    y_pix = (geom.GetPoint()[1] - y_origin) / pixel_height

    return (x_pix, y_pix)



def geojson_to_pixel_arr(raster_file, geojson_file, pixel_ints=True,
                       verbose=False):
    '''
    Tranform geojson file into array of points in pixel (and latlon) coords
    pixel_ints = 1 sets pixel coords as integers
    '''
    
    # load geojson file
    with open(geojson_file) as f:
        geojson_data = json.load(f)

    # load raster file and get geo transforms
    src_raster = gdal.Open(raster_file)
    targetsr = osr.SpatialReference()
    targetsr.ImportFromWkt(src_raster.GetProjectionRef())
        
    geom_transform = src_raster.GetGeoTransform()
    
    # get latlon coords
    latlons = []
    types = []
    for feature in geojson_data['features']:
        coords_tmp = feature['geometry']['coordinates'][0]
        type_tmp = feature['geometry']['type']
        if verbose: 
            print("features:", feature.keys())
            print("geometry:features:", feature['geometry'].keys())

            #print "feature['geometry']['coordinates'][0]", z
        latlons.append(coords_tmp)
        types.append(type_tmp)
        #print feature['geometry']['type']
    
    # convert latlons to pixel coords
    pixel_coords = []
    latlon_coords = []
    for i, (poly_type, poly0) in enumerate(zip(types, latlons)):
        
        if poly_type.upper() == 'MULTIPOLYGON':
            #print "oops, multipolygon"
            for poly in poly0:
                poly=np.array(poly)
                if verbose:
                    print("poly.shape:", poly.shape)
                    
                # account for nested arrays
                if len(poly.shape) == 3 and poly.shape[0] == 1:
                    poly = poly[0]
                    
                poly_list_pix = []
                poly_list_latlon = []
                if verbose: 
                    print("poly", poly)
                for coord in poly:
                    if verbose: 
                        print("coord:", coord)
                    lon, lat, z = coord 
                    px, py = latLon2pixel(lat, lon, input_raster=src_raster,
                                         targetsr=targetsr, 
                                         geomTransform=geom_transform)
                    poly_list_pix.append([px, py])
                    if verbose:
                        print("px, py", px, py)
                
                if pixel_ints:
                    ptmp = np.rint(poly_list_pix).astype(int)
                else:
                    ptmp = poly_list_pix
                pixel_coords.append(ptmp)
                latlon_coords.append(poly_list_latlon)            

        elif poly_type.upper() == 'POLYGON':
            poly=np.array(poly0)
            if verbose:
                print("poly.shape:", poly.shape)
                
            # account for nested arrays
            if len(poly.shape) == 3 and poly.shape[0] == 1:
                poly = poly[0]
                
            poly_list_pix = []
            poly_list_latlon = []
            if verbose: 
                print("poly", poly)
            for coord in poly:
                if verbose: 
                    print("coord:", coord)
                lon, lat, z = coord 
                px, py = gT.latLonToPixel(lat, lon, input_raster=src_raster,
                                     targetsr=targetsr, 
                                     geomTransform=geom_transform)
                poly_list_pix.append([px, py])
                if verbose:
                    print("px, py", px, py)
                poly_list_latlon.append([lat, lon])
            
            if pixel_ints:
                ptmp = np.rint(poly_list_pix).astype(int)
            else:
                ptmp = poly_list_pix
            pixel_coords.append(ptmp)
            latlon_coords.append(poly_list_latlon)
            
        else:
            print("Unknown shape type in coords_arr_from_geojson()")
            return
            
    return pixel_coords, latlon_coords

