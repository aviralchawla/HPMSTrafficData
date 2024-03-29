"""

HPMS Data Project - Near-Road Exposure

Last Updated: 03/19/2024
Created by Brittany Antonczak and Meg Fay
University of Vermont, Burlington, VT

"""


############################## ABOUT THIS SCRIPT ##############################
#                                                                             #
# This script converts the HPMS road link AADT estimation results to spatial  #
# data by joining HPMS road link AADT estimation results to the HPMS road     #
# network geodatabase feature class.                                          #                   
#                                                                             #
# Approximate script total execution time: --- 37 minutes --- (02/28/2024)    #
#                                                                             #
############################## ABOUT THIS SCRIPT ##############################
 

# script title
print('''--- HPMS Data Project - Near-Road Exposure ---''','\n')

# import packages 
import arcpy
import time
import datetime
import sys
import numpy as np

# overwrite existing files (False = No, True = Yes)
arcpy.env.overwriteOutput = True
print('arcpy.env.overwriteOutput', arcpy.env.overwriteOutput,'\n')


########################### USER-DEFINED VARIABLES ############################

# set input file paths:
# HPMS road network feature class:
geo_in_path = "Z:/ROAD_AQ/HPMS Traffic Data/HPMS/HPMS_test.gdb/HPMS_2018_county_intxn"
# HPMS road link AADT estimation results table:
tab_in_path = "Z:/ROAD_AQ/HPMS Traffic Data/HPMS/Imputed AADT/hpms_aadt_imputed_new.csv"

# set join field 
geo_join_field = "FID_Link_Cnty_Intxn"
tab_join_field = "FID_Link_Cnty_Intxn"

# set name of output feature class
out_name = "hpms_aadt_imputation"

# set coordinate system of output data:
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("USA Contiguous Albers Equal Area Conic USGS")

# set output geodatabase:
out_gdb = "Z:/ROAD_AQ/HPMS Traffic Data/HPMS/HPMS_test.gdb"


########################### DEFINED FUNCTIONS #################################

# define function to print feature class field names
def getFieldNames(in_table):
        field_names = [f.name for f in arcpy.ListFields(in_table)]
        return field_names

# define function for generating list of unique values in a feature class field
def getUniqueValues(in_table, field_name):
    # use SearchCursor to return a set of unique field values
    with arcpy.da.SearchCursor(in_table, [field_name]) as cursor:
        return sorted({row[0] for row in cursor})

def queryBuilder(values_field, values_list):
    single_string = ''
    for value in values_list:
        single_string += '{} = {} Or '.format(values_field, value)
    return single_string[:-4]

###############################################################################

# ----- START OF ANALYSIS ----- # 


# print current date and time
dt = datetime.datetime.now()
print ("Current date and time:",dt.strftime("%Y-%m-%d %H:%M:%S"),'\n\n')

# set start time for total execution time calculation
start_time_total = time.time()


###############################################################################
# General Overview of Analysis Steps:                                         
###############################################################################

# Step 1. Import results table to geodatabase. 
#      >> arcpy.conversion.TableToTable()
# Step 2. Create new geometry feature class to store results.
#      >> arcpy.FieldMappings()
#      >> arcpy.FeatureClassToFeatureClass_conversion()
# Step 3. Join results to new geometry feature class.
#      >> arcpy.JoinField_JoinField() *imported toolbox

###############################################################################


###############################################################################
# Step 1. Import results table to geodatabase. 
###############################################################################

# set start time for execution time calculation
start_time = time.time()

# set local variables
in_table = tab_in_path
tab_out_gdb = out_gdb
tab_out_name = out_name + "_table"

try:
        # execute TableToTable
        if arcpy.Exists(tab_out_gdb + "\\" + tab_out_name):
                arcpy.Delete_management(tab_out_gdb + "\\" + tab_out_name)
        arcpy.conversion.TableToTable(in_table, tab_out_gdb, tab_out_name)
        print('Imported results table to the following path:\n{}'.format(tab_out_gdb + "\\" + tab_out_name))
        print('Execution time: --- %s minutes ---\n' % round(((time.time() - start_time)*(1/60)))) 

except Exception as e:
        # print error messages
        print(arcpy.GetMessages())
        print("ERROR: ")
        print(e)
        sys.exit('Exiting script.')
        

###############################################################################
# Step 2. Create new geometry feature class to store results.
###############################################################################

# set start time for execution time calculation
start_time = time.time()

# set local variables
in_feature = geo_in_path
keep_fields = [str(geo_join_field),'Shape_Length']
geo_out_gdb = out_gdb
geo_out_name = out_name

try:
        # map fields
        field_mappings = arcpy.FieldMappings()
        for field in keep_fields:
                fmap = arcpy.FieldMap()
                fmap.addInputField(in_feature, field) 
                fmap.mergeRule = "First"
                field_mappings.addFieldMap(fmap)
        
        # execute FeatureClassToFeatureClass_conversion
        arcpy.FeatureClassToFeatureClass_conversion(in_feature, geo_out_gdb, geo_out_name, '', field_mapping = field_mappings)
        print('Generated new geometry feature class:\n{}'.format(geo_out_gdb + "\\" + geo_out_name))
        print('Execution time: --- %s minutes ---\n' % round(((time.time() - start_time)*(1/60)))) 

except Exception as e:
        # print error messages
        print(arcpy.GetMessages())
        print("ERROR: ")
        print(e)
        sys.exit('Exiting script.')

    
###############################################################################
# Step 3. Join results to new geometry feature class.
###############################################################################

# set start time for execution time calculation
start_time = time.time()

# set local variables
in_feature = geo_out_gdb + '\\' + geo_out_name
join_table = tab_out_gdb + '\\' + tab_out_name
#getFieldNames(in_feature)
#getFieldNames(join_table)
in_field = str(geo_join_field)
join_field = str(tab_join_field)
fields = getFieldNames(join_table)
field_remove = ['OBJECTID','Shape_Length','Shape_Area',join_field]
for field in field_remove:
        if field in fields: fields.remove(field)

try:
        # execute JoinField
        arcpy.management.JoinField(in_feature, in_field, join_table, join_field, fields)
        print('Joined the following results fields to the geometry feature class:\n{}'.format(fields))
        print('Execution time: --- %s minutes ---\n' % round(((time.time() - start_time)*(1/60)))) 
    
except Exception as e:
        # print error messages
        print(arcpy.GetMessages())
        print("ERROR: ")
        print(e)
        sys.exit('Exiting script.')
        

# print total execution time calculation 
print('Total Execution time: --- %s minutes ---\n' % round(((time.time() - start_time_total)*(1/60))))


# ----- END OF SCRIPT ----- #
print('----- END OF SCRIPT -----')
