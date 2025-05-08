#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Exploratory ETL for SpaceNet SN2 (AOI 2 Vegas).
Adds debug prints to trace file counts and paths.
"""

import os, sys, glob, shutil
import matplotlib.pyplot as plt
import numpy as np
import rasterio
####################
# EDIT THESE PATHS
spacenet_data_dir = os.path.expanduser("~/spacenet/SN2_buildings")
TRAIN_AOI = "AOI_2_Vegas_Train"
# Build your imagery & vector paths
imDir  = os.path.join(spacenet_data_dir, "training", TRAIN_AOI, "RGB-PanSharpen")
vecDir = os.path.join(spacenet_data_dir, "training", TRAIN_AOI, "geojson", "buildings") # there is a sub directory called buildings 

# Output root (next to this script)
spacenet_explore_dir = os.path.dirname(os.path.realpath(__file__))

# How many images to demo
N_ims = 15

# Verify input dirs
for p in (imDir, vecDir):
    if not os.path.isdir(p):
        raise FileNotFoundError("Expected folder not found: %s" % p)
    else:
        print("Found folder:", p)

# Import local ETL modules
sys.path.insert(0, spacenet_explore_dir)
import geojson_to_pixel_arr, create_dist_map, create_building_mask, \
       plot_truth_coords, plot_building_mask, plot_dist_transform, \
       plot_all_transforms

def main():
    # 1) Prepare output directories
    dirs = {
      "images_out": os.path.join(spacenet_explore_dir, "3band"),
      "coords_demo": os.path.join(spacenet_explore_dir, "pixel_coords_demo"),
      "mask": os.path.join(spacenet_explore_dir, "building_mask"),
      "mask_vis": os.path.join(spacenet_explore_dir, "building_mask_vis"),
      "mask_demo": os.path.join(spacenet_explore_dir, "mask_demo"),
      "dist": os.path.join(spacenet_explore_dir, "distance_trans"),
      "dist_demo": os.path.join(spacenet_explore_dir, "distance_trans_demo"),
      "all_demo": os.path.join(spacenet_explore_dir, "all_demo"),
    }
    for name, path in dirs.items():
        if not os.path.exists(path):
            os.makedirs(path)
            print("Created dir [%s]: %s" % (name, path))
        else:
            print("Output dir exists [%s]: %s" % (name, path))

    # 2) Copy a sample of images to images_out
    raster_list = sorted(glob.glob(os.path.join(imDir, "*.tif")))
    if not raster_list:
        print("ERROR: no .tif files found in:", imDir)
        return
    demo_list = raster_list[10:10+N_ims]
    print("Selected %d demo images from %d total" % (len(demo_list), len(raster_list)))
    for src in demo_list:
        dst = os.path.join(dirs["images_out"], os.path.basename(src))
        shutil.copy(src, dst)
    print("Copied demo images to:", dirs["images_out"])

    # 3) Process each demo image
    for i, rasterSrc in enumerate(demo_list):
        print("\n=== [%d/%d] Processing %s ===" % (i+1, len(demo_list), rasterSrc))
        with rasterio.open(rasterSrc) as src:
            # Read the first three bands (R, G, B) into a H×W×3 array
            img = src.read([1,2,3])                # → shape (3, H, W)
            img = img.transpose(1,2,0)             # → shape (H, W, 3)

            # Derive names and paths
            name_root0 = os.path.splitext(os.path.basename(rasterSrc))[0]
            # The numeric ID part: e.g. "AOI_2_Vegas_img1010"
            # (you can also keep the full name and just prepend "buildings_")
            aoi_part = name_root0.split("_", 1)[1]  
            # Build the actual GeoJSON filename:
            json_name = f"buildings_{aoi_part}.geojson"
            # Point into the 'buildings' subfolder:
            vectorSrc = os.path.join(vecDir, json_name)
            
            if not os.path.isfile(vectorSrc):
                print(f"  WARNING: geojson not found: {vectorSrc}")
                continue
            # making sure botoh the files exist, printed above
            print("  → Found vector file:", vectorSrc)
            # 3a) Pixel coords
            pixel_coords, latlon_coords = geojson_to_pixel_arr.geojson_to_pixel_arr(
                rasterSrc, vectorSrc, pixel_ints=True, verbose=False
            )
            print("  → pixel_coords:", len(pixel_coords), "polygons")

            out_png = os.path.join(dirs["coords_demo"], name_root + ".png")
            plot_truth_coords.plot_truth_coords(
                img, pixel_coords, figsize=(8,8), plot_name=out_png, add_title=False
            )
            print("  → saved coords demo:", out_png)

            # 3b) Building masks
            tif_mask = os.path.join(dirs["mask"], name_root0 + ".tif")
            tif_mask_vis = os.path.join(dirs["mask_vis"], name_root0 + ".tif")
            create_building_mask.create_building_mask(
                rasterSrc, vectorSrc, npDistFileName=tif_mask, burn_values=1
            )
            create_building_mask.create_building_mask(
                rasterSrc, vectorSrc, npDistFileName=tif_mask_vis, burn_values=255
            )
            print("  → masks wrote:", tif_mask, "and", tif_mask_vis)

            out_png2 = os.path.join(dirs["mask_demo"], name_root + ".png")
            mask_img = plt.imread(tif_mask)
            plot_building_mask.plot_building_mask(
                img, pixel_coords, mask_img, figsize=(8,8),
                plot_name=out_png2, add_title=False
            )
            print("  → saved mask demo:", out_png2)

            # 3c) Distance transform
            np_dist = os.path.join(dirs["dist"], name_root0 + ".npy")
            create_dist_map.create_dist_map(
                rasterSrc, vectorSrc, npDistFileName=np_dist,
                noDataValue=0, burn_values=1, dist_mult=1, vmax_dist=64
            )
            print("  → distance map npy:", np_dist)

            out_png3 = os.path.join(dirs["dist_demo"], name_root + ".png")
            dist_img = np.load(np_dist)
            plot_dist_transform.plot_dist_transform(
                img, pixel_coords, dist_img, figsize=(8,8),
                plot_name=out_png3, add_title=False, colorbar=True
            )
            print("  → saved dist demo:", out_png3)

            # 3d) All transforms
            out_png4 = os.path.join(dirs["all_demo"], name_root + ".png")
            plot_all_transforms.plot_all_transforms(
                img, pixel_coords, plt.imread(tif_mask), dist_img,
                figsize=(8,8), plot_name=out_png4,
                add_global_title=False, colorbar=False,
                add_titles=False, poly_face_color='orange',
                poly_edge_color='red', poly_nofill_color='blue',
                cmap='bwr'
            )
            print("  → saved all_demo:", out_png4)

    print("\nDone.")
    

if __name__ == "__main__":
    main()

