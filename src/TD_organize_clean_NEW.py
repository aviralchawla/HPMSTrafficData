"""
HPMS Data Paper
by Aviral Chawla, Meg Fay, and Britanny Antonczak

Summary: This script 
1) Merges state-level census block feature classes into a single national feature class,
2) Copies HPMS imputation to Traffic Desnity gdb,
3) Constructs buffers around census blocks at a distance of 250m outward from census block boundaries, and
4) Intersects census blocks buffers with roads.

<LICENSE>
"""

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

# file path to Traffic Density geodatabase
TD_gdb = "relative path to Traffic Density geodatabase"

# file path to HPMS data geodatabase
HPMS_gdb = "relative path to HPMS data geodatabase"

# ----- LOAD DATA --------------------------------------------------------------
print("Loading data...")

# remove scientific notation 
pd.set_option('display.float_format', '{:.4f}'.format)

# check that all file paths exist
file_paths = [TD_gdb, HPMS_gdb]

for file_path in file_paths:
    if not os.path.exists(file_path):
        print(f"ERROR: The file or directory does not exist: {file_path}")
        sys.exit()
    else: 
        print(f"File or directory exists: {file_path}") 

# ----- START ----- # 

# >>> Create national feaure class of census blocks <<<
        
# Set the workspace to the census block geodatabase
arcpy.env.workspace = TD_gdb

# Merge all the state census block feature classes into a single national feature class
print("Merging state census block feature classes...")

# List of state feature classes in the source geodatabase
state_fcs = arcpy.ListFeatureClasses()

# Merge the state feature classes
inputs = state_fcs
output = f"{TD_gdb}\\US_census_block_2020"
try:
    arcpy.Merge_management(inputs, output)
    print("State census block feature classes merged.")
except Exception as e:
    print(f"ERROR: The feature classes could not be merged. {e}")

# Calculate area of each census block
print("Calculating area of each census block...")
in_table = f"{TD_gdb}\\US_census_block_2020"
field_name = "Area_Orig"
field_type = "DOUBLE"
try:
    # Add a field to store the land area
    arcpy.AddField_management(in_table, field_name, field_type)
    print("Land area field added.")
except Exception as e:
    print(f"ERROR: The land area field could not be added. {e}")

in_feature = f"{TD_gdb}\\US_census_block_2020"
geometry_property = [[field_name, "AREA"]]
length_unit = ''
area_unit = "SQUARE_METERS"
try:
    arcpy.management.CalculateGeometryAttributes(in_feature, geometry_property, length_unit, area_unit)
    print('Calculated new field for intersection area: {}'.format(field_name))


except Exception as e:
    # print error messages
    print(arcpy.GetMessages())
    print("ERROR: ")
    print(e)
    sys.exit('Exiting script.')    

# >>> Copy HPMS feature classes to the new geodatabase <<<

print("Copying HPMS data to geodatabase...")

# Feature class names in the source and target geodatabases
fc_HPMS = "HPMS_2018_vmt"
in_data = f"{HPMS_gdb}\\{fc_HPMS}"
out_data = f"{TD_gdb}\\{fc_HPMS}"

# Copy the feature classes
try:
    arcpy.Copy_management(in_data, out_data)
    print("HPMS data copied to geodatabase.")
except Exception as e:
    print(f"ERROR: The feature class could not be copied. {e}")

########################### USER-DEFINED VARIABLES ############################

# set input census block buffer distance to be evaluated:
distance = 250

# Print buffer distance
print('Buffer distance: {} Meters\n'.format(str(distance)))

# set input census blocks file path:
blocks_in_path = "Z:/ROAD_AQ/HPMS Traffic Data/HPMS/TD_test.gdb/US_census_block_2020"

# set output geodatabase:
out_gdb = "Z:/ROAD_AQ/HPMS Traffic Data/HPMS/TD_test.gdb"

########################### START BUFFER BLOCKS ############################

# >>> buffer census blocks feature class <<<

# set local variables
in_feature = TD_gdb + '\\' + "US_census_block_2020"
out_feature = TD_gdb + '\\' + "US_census_block_buffers"
buffer_distance = str(distance) + " Meters"
dissolve_option = "NONE"
dissolve_field = None
method = "PLANAR"
max_deviation = "0 Meters"
try:
    # execute PairwiseBuffer
    arcpy.analysis.PairwiseBuffer(in_feature, out_feature, buffer_distance, dissolve_option, dissolve_field, method, max_deviation)
    print('Generated new buffer feature class:\n{}'.format(out_feature))

except Exception as e:
    # print error messages
    print(arcpy.GetMessages())
    print("ERROR: ")
    print(e)
    sys.exit('Exiting script.')


# >>> calculate new field for buffer area <<<

# set local variables
in_feature = out_feature
field_name = "Area_Buffer"
field_type = "DOUBLE"
try:
    # execute AddField and CalculateGeometryAttributes
    arcpy.management.AddField(in_feature, field_name, field_type)
    print('Added new field for buffer area: {}'.format(field_name))
except Exception as e:
    # print error messages
    print(arcpy.GetMessages())
    print("ERROR: ")
    print(e)
    sys.exit('Exiting script.')

geometry_property = [[field_name, "AREA"]]
length_unit = ''
area_unit = "SQUARE_METERS"
try:
    arcpy.management.CalculateGeometryAttributes(in_feature, geometry_property, length_unit, area_unit)
    print('Calculated new field for intersection area: {}'.format(field_name))

except Exception as e:
    # print error messages
    print(arcpy.GetMessages())
    print("ERROR: ")
    print(e)
    sys.exit('Exiting script.')

#################### END OF BUFFER BLOCKS ####################

#################### START OF INTERSECT BUFFER AND ROADS ####################

# set path of geodatabase containing input road buffer feature classes:
buffs_fc = f"{TD_gdb}\\US_census_block_buffers"

# set path of input census block feature class:
roads_fc = f"{TD_gdb}\\HPMS_2018_vmt"

# >>> intersect census block buffers and roads feature classes <<<
        
# set local variables
in_fcs = [buffs_fc, roads_fc]
out_fc = out_gdb + "\\" + 'density_intxn' 

try:
    # execute PairwiseIntersect
    arcpy.analysis.PairwiseIntersect(in_fcs, out_fc)
    print('Intersected census block buffers and roads feature classes to the following path:\n{}'.format(out_fc))

except Exception as e:
    # print error messages
    print(arcpy.GetMessages())
    print("ERROR: ")
    print(e)
    sys.exit('Exiting script.')            

# ----- END OF SCRIPT ----- #
print('----- END OF SCRIPT -----')   


