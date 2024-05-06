"""
HPMS Data Paper
by Aviral Chawla, Meg Fay, and Britanny Antonczak

Summary: This script 
1) This script converts the HPMS road link AADT estimation results to spatial data,
2) Calculates the length of road segments in miles and kilometers, and 
3) Calculates the vehicle miles traveled (VMT) and vehicle kilometers traveled (VKT) for all vehicle classes.

<LICENSE>
"""

# import packages 
import arcpy
import time
import datetime
import sys
import numpy as np

# overwrite existing files (False = No, True = Yes)
arcpy.env.overwriteOutput = True
print('arcpy.env.overwriteOutput', arcpy.env.overwriteOutput,'\n')

# set coordinate system of output data:
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("USA Contiguous Albers Equal Area Conic USGS")

########################### USER-DEFINED VARIABLES ############################

# set input file paths:
# HPMS road network feature class:
geo_in_path = "relative file path to HPMS.gdb and HPMS_2018_county_intxn feature class"
# HPMS road link AADT estimation results table:
tab_in_path = "relative path to hpms_aadt_imputed_new.csv" # or whatever the result of the imputation is called

# set join field 
geo_join_field = "FID_Link_Cnty_Intxn"
tab_join_field = "FID_Link_Cnty_Intxn"

# set name of output feature class
out_name = "hpms_aadt_imputation"

# set output geodatabase:
out_gdb = "relative path to HPMS.gdb"


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

except Exception as e:
        # print error messages
        print(arcpy.GetMessages())
        print("ERROR: ")
        print(e)
        sys.exit('Exiting script.')

    
###############################################################################
# Step 3. Join results to new geometry feature class.
###############################################################################

# set local variables
in_feature = geo_out_gdb + '\\' + geo_out_name
join_table = tab_out_gdb + '\\' + tab_out_name
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
    
except Exception as e:
        # print error messages
        print(arcpy.GetMessages())
        print("ERROR: ")
        print(e)
        sys.exit('Exiting script.')
        
###############################################################################
# Step 4. Calculate geometry length in meters.
###############################################################################

# Calculate length of each road link in meters
print("Calculating length of each road link in meters...")
in_table = f"{out_gdb}\\hpms_aadt_imputation"
field_name = "Shape_Length="
field_type = "DOUBLE"
try:
    # Add a field to store the land area
    arcpy.AddField_management(in_table, field_name, field_type)
except Exception as e:
    arcpy.GetMessages()
    print("ERROR: ")
    print(e)
    sys.exit('Exiting script.')

in_feature = f"{out_gdb}\\hpms_aadt_imputation"
geometry_property = [[field_name, "LENGTH"]]
length_unit = "METERS"
area_unit = ''
try:
    arcpy.management.CalculateGeometryAttributes(in_feature, geometry_property, length_unit, area_unit)
    print('Calculated new field for intersection area: {}'.format(field_name))
except Exception as e:
    # print error messages
    print(arcpy.GetMessages())
    print("ERROR: ")
    print(e)
    sys.exit('Exiting script.')


###############################################################################
# Step 5. Calculate VMT and VKT for all vehicle classes.
###############################################################################

# add VMT and VKT fields for each vehicle class
in_table = f"{out_gdb}\\hpms_aadt_imputation"
field_type = "DOUBLE"
field_names = ['VMT_MDV', 'VKT_MDV', 'VMT_HDV', 'VKT_HDV', 'VMT_TOTAL', 'VKT_TOTAL']
for field_name in field_names:
    try:
        arcpy.AddField_management(in_table, field_name, field_type)
    except Exception as e:
        arcpy.GetMessages()
        print("ERROR: ")
        print(e)
        sys.exit('Exiting script.')

# calculate VMT and VKT for each vehicle class
print("Calculating VMT and VKT for each vehicle class...")
arcpy.CalculateField_management(in_table, 'VMT_MDV', '!AADT_MDV! * (!Shape_Length! / 1609.34)', "PYTHON3")
arcpy.CalculateField_management(in_table, 'VKT_MDV', '!AADT_MDV! * (!Shape_Length! / 1000)', "PYTHON3")

arcpy.CalculateField_management(in_table, 'VMT_HDV', '!AADT_HDV! * (!Shape_Length! / 1609.34)', "PYTHON3")
arcpy.CalculateField_management(in_table, 'VKT_HDV', '!AADT_HDV! * (!Shape_Length! / 1000)', "PYTHON3")

arcpy.CalculateField_management(in_table, 'VMT_TOTAL', '!AADT! * (!Shape_Length! / 1609.34)', "PYTHON3")
arcpy.CalculateField_management(in_table, 'VKT_TOTAL', '!AADT! * (!Shape_Length! / 1000)', "PYTHON3")

# ----- END OF SCRIPT ----- #
print('----- END OF SCRIPT -----')
