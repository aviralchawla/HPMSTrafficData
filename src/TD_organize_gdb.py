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
--- Near-Road Exposure: Traffic Density File Geodatabase Preparation ---''','\n')

# import packages 
import arcpy
import time
import datetime
import sys
import os
import numpy as np
import pandas as pd

# overwrite existing files (False = No, True = Yes)
arcpy.env.overwriteOutput = True
print('arcpy.env.overwriteOutput', arcpy.env.overwriteOutput,'\n')

# set coordinate system of output data:
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("USA Contiguous Albers Equal Area Conic USGS")

########################### USER-DEFINED VARIABLES ############################

# specify the output path for the project gdb
gdb_folder_path = "Z:/ROAD_AQ/HPMS Traffic Data/HPMS"

# name project gdb
gdb_name = "TD_test.gdb"

# file path to HPMS data geodatabase
HPMS_source_gdb = "Z:/ROAD_AQ/HPMS Traffic Data/HPMS/HPMS_test.gdb"

# file paths to the raw Census feature classes
block_source_gdb = "Z:/ROAD_AQ/HPMS Traffic Data/Census Boundaries/2020_Census_Block_Boundaries.gdb"

# ----- LOAD DATA --------------------------------------------------------------
print("Loading data...")

# remove scientific notation 
pd.set_option('display.float_format', '{:.4f}'.format)

# check that all file paths exist
file_paths = [gdb_folder_path, HPMS_source_gdb, block_source_gdb]

for file_path in file_paths:
    if not os.path.exists(file_path):
        print(f"ERROR: The file or directory does not exist: {file_path}")
        sys.exit()
    else: 
        print(f"File or directory exists: {file_path}") 

# ----- START ----- # 
        
# >>> Create national feaure class of census blocks <<<
        
# Set the workspace to the census block geodatabase
arcpy.env.workspace = block_source_gdb

# Merge all the state census block feature classes into a single national feature class
print("Merging state census block feature classes...")

# List of state feature classes in the source geodatabase
state_fcs = arcpy.ListFeatureClasses()

# Merge the state feature classes
try:
    arcpy.Merge_management(state_fcs, f"{block_source_gdb}\\US_census_block_2020")
    print("State census block feature classes merged.")
except Exception as e:
    print(f"ERROR: The feature classes could not be merged. {e}")

# Calculate land area of each census block
print("Calculating land area of each census block...")
try:
    # Add a field to store the land area
    arcpy.AddField_management(f"{block_source_gdb}\\US_census_block_2020", "Area_Land_Orig", "DOUBLE")
    # Calculate the field as equal to field ALAND20
    arcpy.CalculateField_management(f"{block_source_gdb}\\US_census_block_2020", "Area_Land_Orig", "!ALAND20!", "PYTHON3")
    print("Land area calculated.")
except Exception as e:
    print(f"ERROR: The land area could not be calculated. {e}")
        
# >>> Create new file geodatabase <<<

# Use the CreateFileGDB_management tool to create the new project geodatabase
arcpy.CreateFileGDB_management(gdb_folder_path, gdb_name)
print(f"Geodatabase {gdb_name} created.")
TD_target_gdb = os.path.join(gdb_folder_path, gdb_name)

# Set the workspace to the traffic density geodatabase
arcpy.env.workspace = TD_target_gdb     

# --- END SCRIPT UNTIL HPMS IS COMPLETE ---
sys.exit()

# >>> Copy HPMS feature classes to the new geodatabase <<<

print("Copying HPMS data to geodatabase...")

# Feature class names in the source and target geodatabases
fc_HPMS = "NAME TBD"

# Copy the feature classes
try:
    arcpy.Copy_management(f"{HPMS_source_gdb}\\{fc_HPMS}", f"{TD_target_gdb}\\{fc_HPMS}")
    print("HPMS data copied to geodatabase.")
except Exception as e:
    print(f"ERROR: The feature class could not be copied. {e}")

# >>> Copy Census feature class to the new geodatabase <<<

print("Copying Census data to geodatabase...")

# Feature class names in the source and target geodatabases
fc_block = "tl_2020_us_county"
fc_block_new = "US_census_block_2020"

# Copy the feature classes
try:
    arcpy.Copy_management(f"{block_source_gdb}\\{fc_block}", f"{TD_target_gdb}\\{fc_block_new}")
    print("Census block data copied to geodatabase.")
except Exception as e:
    print(f"ERROR: The feature classes could not be copied. {e}")

    
print('----- END OF SCRIPT -----')
