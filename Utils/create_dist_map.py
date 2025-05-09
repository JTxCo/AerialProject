#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
See https://github.com/SpaceNetChallenge/utilities/tree/master/python/spaceNet 
for more code
'''

from osgeo import gdal, ogr, gdalnumeric
# Used GDAL instead of rasterio. Converted for ease of use and consistency
import rasterio as rio 
import numpy as np
import sys
import os
####################
# download spacenet utilities from above link
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
#from spaceNet import labelTools as lT

###############################################################################
def create_dist_map(rasterSrc, vectorSrc, npDistFileName='', 
                           noDataValue=0, burn_values=1, 
                           dist_mult=1, vmax_dist=64):

    '''
    Create building signed distance transform from Yuan 2016 
    (https://arxiv.org/pdf/1602.06564v1.pdf).
    vmax_dist: absolute value of maximum distance (meters) from building edge
    Adapted from createNPPixArray in labeltools
    '''
    
    ## open source vector file that truth data
    source_ds = ogr.Open(vectorSrc)
    source_layer = source_ds.GetLayer()

    ## extract data from src Raster File to be emulated
    ## open raster file that is to be emulated
    srcRas_ds = gdal.Open(rasterSrc)
    cols = srcRas_ds.RasterXSize
    rows = srcRas_ds.RasterYSize

    # Opening and using rasterio to get the geotransform
    with rio.open(rasterSrc) as src_rio:
        geoTrans, poly, ulX, ulY, lrX, lrY = gT.getRasterExtent(src_rio)
    line = ogr.Geometry(ogr.wkbLineString)
    line.AddPoint(geoTrans[0], geoTrans[3])
    line.AddPoint(geoTrans[0]+geoTrans[1], geoTrans[3])

    metersIndex = abs(geoTrans[1])


    memdrv = gdal.GetDriverByName('MEM')
    dst_ds = memdrv.Create('', cols, rows, 1, gdal.GDT_Byte)
    dst_ds.SetGeoTransform(srcRas_ds.GetGeoTransform())
    dst_ds.SetProjection(srcRas_ds.GetProjection())
    band = dst_ds.GetRasterBand(1)
    band.SetNoDataValue(noDataValue)

    gdal.RasterizeLayer(dst_ds, [1], source_layer, burn_values=[burn_values])
    srcBand = dst_ds.GetRasterBand(1)

    memdrv2 = gdal.GetDriverByName('MEM')
    prox_ds = memdrv2.Create('', cols, rows, 1, gdal.GDT_Int16)
    prox_ds.SetGeoTransform(srcRas_ds.GetGeoTransform())
    prox_ds.SetProjection(srcRas_ds.GetProjection())
    proxBand = prox_ds.GetRasterBand(1)
    proxBand.SetNoDataValue(noDataValue)

    opt_string = 'NODATA='+str(noDataValue)
    options = [opt_string]

    gdal.ComputeProximity(srcBand, proxBand, options)

    memdrv3 = gdal.GetDriverByName('MEM')
    proxIn_ds = memdrv3.Create('', cols, rows, 1, gdal.GDT_Int16)
    proxIn_ds.SetGeoTransform(srcRas_ds.GetGeoTransform())
    proxIn_ds.SetProjection(srcRas_ds.GetProjection())
    proxInBand = proxIn_ds.GetRasterBand(1)
    proxInBand.SetNoDataValue(noDataValue)
    opt_string2 = 'VALUES='+str(noDataValue)
    options = [opt_string, opt_string2]
    #options = ['NODATA=0', 'VALUES=0']

    gdal.ComputeProximity(srcBand, proxInBand, options)

    proxIn = gdalnumeric.BandReadAsArray(proxInBand)
    proxOut = gdalnumeric.BandReadAsArray(proxBand)

    proxTotal = proxIn.astype(float) - proxOut.astype(float)
    proxTotal = proxTotal*metersIndex
    proxTotal *= dist_mult

    # clip array
    proxTotal = np.clip(proxTotal, -1*vmax_dist, 1*vmax_dist)

    if npDistFileName != '':
        # save as numpy file since some values will be negative
        np.save(npDistFileName, proxTotal)
        #cv2.imwrite(npDistFileName, proxTotal)

    #return proxTotal
    return
