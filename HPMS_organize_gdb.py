"""

HPMS Data Project - Near-Road Exposure

Last Updated: 02/21/2023
Created by Meg Fay
University of Vermont, Burlington, VT

"""

############################## ABOUT THIS SCRIPT ##############################
#                                                                             #
# This script copies the raw HPMS and Census feature classes to a single      #
# geodatabase for cleaning the HPMS data.                                     #
#                                                                             #
############################## ABOUT THIS SCRIPT ##############################

# script title
print('''
--- Near-Road Exposure: HPMS File Geodatabase Preparation ---''','\n')

# import packages 
import arcpy
import geopandas as gpd
import pandas as pd
import pyogrio
import pyarrow
import time
import datetime
import sys
import os

# overwrite existing files (False = No, True = Yes)
arcpy.env.overwriteOutput = True
print('arcpy.env.overwriteOutput', arcpy.env.overwriteOutput,'\n')

########################### USER-DEFINED VARIABLES ############################

# >>> Create new file geodatabase <<<

# specify the output path for the project gdb
gdb_folder_path = "C:/Users/mrfay/OneDrive - University of Vermont/Documents/LOCAL"

# name project gdb
gdb_name = "HPMS_test.gdb"

# file path to raw HPMS gdb
HPMS_path = "Z:/ROAD_AQ/HPMS Traffic Data/Downloaded Data/NTAD2019_GDB_HPMS2018_2019_10_21/NTAD2019_GDB_HPMS2018_2019_10_21.gdb"

# file paths to the raw Census shapefiles
census_county_path = "Z:/ROAD_AQ/HPMS Traffic Data/Downloaded Data/2020 Census County Boundaries/tl_2020_us_county.shp"
census_uac_path = "Z:/ROAD_AQ/HPMS Traffic Data/Downloaded Data/2020 Census Urban AC Boundaries/tl_rd22_us_uac20.shp"

# ----- LOAD DATA --------------------------------------------------------------
print("Loading data...")

# remove scientific notation 
pd.set_option('display.float_format', '{:.4f}'.format)

# check that all file paths exist
file_paths = [gdb_folder_path, HPMS_path, census_county_path, census_uac_path]

for file_path in file_paths:
    if not os.path.exists(file_path):
        print(f"ERROR: The file or directory does not exist: {file_path}")
        sys.exit()
    else: 
        print(f"File or directory exists: {file_path}") 

# Load data using geopandas
try: 
    # load raw HPMS feature classes
    data_hpms_123 = gpd.read_file(HPMS_path, layer='hpms_2018_fsys123_2019_10_21', engine="pyogrio", use_arrow=True)
    data_hpms_456 = gpd.read_file(HPMS_path, layer='hpms_2018_fsys456_2019_10_21', engine="pyogrio", use_arrow=True)
    print("HPMS data loaded")
    # load input census county data
    data_county = gpd.read_file(census_county_path, engine="pyogrio", use_arrow=True)
    print("census county geometry loaded")
    data_uac = gpd.read_file(census_uac_path, engine="pyogrio", use_arrow=True)
    print("census urban area codes geometry loaded")
except Exception as e:
    print(f"ERROR: The data could not be loaded. {e}")
    print(f"ERROR: The script will terminate.")
    sys.exit()


# ----- START ----- # 

# use the CreateFileGDB_management tool to create the new project geodatabase
arcpy.CreateFileGDB_management(gdb_folder_path, gdb_name)

# List of GeoDataFrames and their corresponding names in the geodatabase
data_list = [(data_hpms_123, 'hpms_2018_fsys123_2019_10_21'), 
             (data_hpms_456, 'hpms_2018_fsys456_2019_10_21'), 
             (data_county, 'US_census_county_2020'), 
             (data_uac, 'US_census_uac_2020')]

# Path to the geodatabase
gdb_path = os.path.join(gdb_folder_path, gdb_name)

# Copy each GeoDataFrame to the geodatabase
for data, name in data_list:
    try:
        # Convert GeoDataFrame to a feature class
        arcpy.CopyFeatures_management(data, os.path.join(gdb_path, name))
        print(f"Feature class {name} copied to geodatabase.")
    except Exception as e:
        print(f"ERROR: The feature class could not be copied. {e}")

