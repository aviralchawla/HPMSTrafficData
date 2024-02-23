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
import pandas as pd
import os
import sys

# overwrite existing files (False = No, True = Yes)
arcpy.env.overwriteOutput = True
print('arcpy.env.overwriteOutput', arcpy.env.overwriteOutput,'\n')

########################### USER-DEFINED VARIABLES ############################

# >>> Create new file geodatabase <<<

# specify the output path for the project gdb
gdb_folder_path = "C:/Users/mrfay/OneDrive - University of Vermont/Documents/LOCAL"

# name project gdb
gdb_name = "HPMS_test.gdb"

# file path to raw data geodatabases
HPMS_source_gdb = "Z:/ROAD_AQ/HPMS Traffic Data/Downloaded Data/NTAD2019_GDB_HPMS2018_2019_10_21/NTAD2019_GDB_HPMS2018_2019_10_21.gdb"
# file paths to the raw Census shapefiles
county_source_gdb = "Z:/ROAD_AQ/HPMS Traffic Data/Census Boundaries/2020_Census_County_Boundaries.gdb"
uac_source_gdb = "Z:/ROAD_AQ/HPMS Traffic Data/Census Boundaries/2010_Census_Urban_AC_Boundaries.gdb"

# ----- LOAD DATA --------------------------------------------------------------
print("Loading data...")

# remove scientific notation 
pd.set_option('display.float_format', '{:.4f}'.format)

# check that all file paths exist
file_paths = [gdb_folder_path, HPMS_source_gdb, county_source_gdb, uac_source_gdb]

for file_path in file_paths:
    if not os.path.exists(file_path):
        print(f"ERROR: The file or directory does not exist: {file_path}")
        sys.exit()
    else: 
        print(f"File or directory exists: {file_path}") 

# ----- START ----- # 

# >>> Create new file geodatabase <<<

# use the CreateFileGDB_management tool to create the new project geodatabase
arcpy.CreateFileGDB_management(gdb_folder_path, gdb_name)
print(f"Geodatabase {gdb_name} created.")
HPMS_target_gdb = os.path.join(gdb_folder_path, gdb_name)
arcpy.env.workspace = HPMS_target_gdb     

# >>> Copy HPMS feature classes to the new geodatabase <<<

print("Copying HPMS data to geodatabase...")

# Feature class names in the source and target geodatabases
fc_123 = "hpms_2018_fsys123_2019_10_21"
fc_456 = "hpms_2018_fsys456_2019_10_21"

# Copy the feature classes
try:
    arcpy.Copy_management(f"{HPMS_source_gdb}\\{fc_123}", f"{HPMS_target_gdb}\\{fc_123}")
    arcpy.Copy_management(f"{HPMS_source_gdb}\\{fc_456}", f"{HPMS_target_gdb}\\{fc_456}")
    print("HPMS data copied to geodatabase.")
except Exception as e:
    print(f"ERROR: The feature class could not be copied. {e}")

# >>> Copy Census feature class to the new geodatabase <<<

print("Copying Census data to geodatabase...")

# Feature class names in the source and target geodatabases
fc_county = "tl_2020_us_county"
fc_cnty_new = "US_census_county_2020"
fc_uac = "tl_2020_us_uac10"
fc_uac_new = "US_census_uac_2010"

# Copy the feature classes
try:
    arcpy.Copy_management(f"{county_source_gdb}\\{fc_county}", f"{HPMS_target_gdb}\\{fc_cnty_new}")
    arcpy.Copy_management(f"{uac_source_gdb}\\{fc_uac}", f"{HPMS_target_gdb}\\{fc_uac_new}")
    print("HPMS data copied to geodatabase.")
except Exception as e:
    print(f"ERROR: The feature classes could not be copied. {e}")


print("Census data copied to geodatabase.")    
print('----- END OF SCRIPT -----')
