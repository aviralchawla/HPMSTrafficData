"""

HPMS Data Project - Near-Road Exposure

Last Updated: 03/29/2024
Created by Brittany Antonczak and Meg Fay
University of Vermont, Burlington, VT

"""

############################## ABOUT THIS SCRIPT ##############################
#                                                                             #
# This script 1) constructs buffers around census blocks at a distance of     #
# 250m outward from census block boundaries and 2) intersects census blocks   #
# buffers with roads.                                                         #
#                                                                             #
############################## ABOUT THIS SCRIPT ##############################

# script title
print('''
--- Near-Road Exposure: Traffic Density Block Intersection Data Preparation ---''','\n')

# import packages 
import arcpy
import time
import datetime
import sys
import numpy as np
import pandas as pd

# overwrite existing files (False = No, True = Yes)
arcpy.env.overwriteOutput = True
print('arcpy.env.overwriteOutput', arcpy.env.overwriteOutput,'\n')

# set coordinate system of output data:
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("USA Contiguous Albers Equal Area Conic USGS")

########################### USER-DEFINED VARIABLES ############################

# set input census block buffer distance to be evaluated:
distance = 250

# Print buffer distance
print('Buffer distance: {} Meters\n'.format(str(distance)))

# set input census blocks file path:
blocks_in_path = "Z:/ROAD_AQ/HPMS Traffic Data/HPMS/TD_test.gdb/US_census_block_2020"

# set output geodatabase:
out_gdb = "Z:/ROAD_AQ/HPMS Traffic Data/HPMS/TD_test.gdb"

# print current date and time
dt = datetime.datetime.now()
print ("Current date and time:",dt.strftime("%Y-%m-%d %H:%M:%S"),'\n\n')

# set start time for total execution time calculation
start_time_total = time.time()

########################### START BUFFER BLOCKS ############################

# >>> buffer census blocks feature class <<<

# set start time for execution time calculation
start_time = time.time()

# set local variables
buffer_distance = str(distance) + " Meters"
in_feature = blocks_in_path
out_feature = out_gdb + '\\' + "US_census_block_buffers"

try:
    # execute PairwiseBuffer
    arcpy.analysis.PairwiseBuffer(in_feature, out_feature, buffer_distance, "NONE", None, "PLANAR", "0 Meters")
    print('Generated new buffer feature class:\n{}'.format(out_feature))
    print('Execution time: --- %s minutes ---\n' % round(((time.time() - start_time)*(1/60)))) 

except Exception as e:
    # print error messages
    print(arcpy.GetMessages())
    print("ERROR: ")
    print(e)
    sys.exit('Exiting script.')


# >>> calculate new field for buffer area <<<

# set start time for execution time calculation
start_time = time.time()

# set local variables
in_feature = out_feature
field_name = "Area_Buffer"
field_type = "DOUBLE"

try:
    # execute AddField and CalculateGeometryAttributes
    arcpy.management.AddField(in_feature, field_name, field_type)
    arcpy.management.CalculateGeometryAttributes(in_feature, [[field_name, "AREA"]], '', "SQUARE_METERS")
    print('Calculated new field for intersection area: {}'.format(field_name))
    print('Execution time: --- %s minutes ---\n' % round(((time.time() - start_time)*(1/60))))

except Exception as e:
    # print error messages
    print(arcpy.GetMessages())
    print("ERROR: ")
    print(e)
    sys.exit('Exiting script.')

#################### END OF BUFFER BLOCKS ####################

#################### START OF INTERSECT BUFFER AND ROADS ####################

# set path of geodatabase containing input road buffer feature classes:
buffs_fc = "Z:/ROAD_AQ/HPMS Traffic Data/HPMS/TD_test.gdb/US_census_block_buffers"

# set path of input census block feature class:
roads_fc = "Z:/ROAD_AQ/HPMS Traffic Data/HPMS/TD_test.gdb/HPMS_2018_vmt"

# >>> intersect census block buffers and roads feature classes <<<

# set start time for execution time calculation
start_time = time.time()
        
# set local variables
in_fcs = [buffs_fc, roads_fc]
out_fc = out_gdb + "\\" + 'density_intxn' 

try:
    # execute PairwiseIntersect
    arcpy.analysis.PairwiseIntersect(in_fcs, out_fc)
    print('Intersected census block buffers and roads feature classes to the following path:\n{}'.format(out_fc))
    print('Execution time: --- %s minutes ---' % round(((time.time() - start_time)*(1/60))))

except Exception as e:
    # print error messages
    print(arcpy.GetMessages())
    print("ERROR: ")
    print(e)
    sys.exit('Exiting script.')


# Print TOTAL geoprocessing execution time
#print('\n','TOTAL Execution Time: --- %s hours ---\n' % round(((time.time() - start_time_total)*(1/(60*60))),2))              


# ----- END OF SCRIPT ----- #
print('----- END OF SCRIPT -----')   


