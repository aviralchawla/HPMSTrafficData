"""

HPMS Data Project - Near-Road Exposure

Last Updated: 02/22/2023
Created by Meg Fay
University of Vermont, Burlington, VT

"""

############################## ABOUT THIS SCRIPT ##############################
#                                                                             #
# This script performs the HPMS cleaning methods outlined in documentation    #
# from Britanny Antonczak using arcpy. Currently, the script cleans and       #
# merges the HPMS network, intersects HPMS links with US census boundaries,   #  
# and adds rural-urban codes to road links in the network.                    #
#                                                                             #
# Approximate total execution time: --- 1 hour --- (02/22/2024)               #
#                                                                             #
############################## ABOUT THIS SCRIPT ##############################

# script title
print('''
--- Near-Road Exposure: HPMS Data Preparation ---''','\n')

# import packages 
import arcpy
import time
import datetime
import sys

# overwrite existing files (False = No, True = Yes)
arcpy.env.overwriteOutput = True
print('arcpy.env.overwriteOutput', arcpy.env.overwriteOutput,'\n')

# If verifying results using ArcGIS GUI -> check basemap
# Coordinate System "USA Contiguous Albers Equal Area Conic USGS"

########################### USER-DEFINED VARIABLES ############################

# Set the workspace
# The default location for geoprocessing tool input and output
arcpy.env.workspace = "Z:/ROAD_AQ/HPMS Traffic Data/HPMS/HPMS_test.gdb"
#arcpy.env.workspace = "C:/Users/mrfay/OneDrive - University of Vermont/Documents/LOCAL/HPMS_test.gdb"

# List all feature classes in the workspace
feature_classes = arcpy.ListFeatureClasses()
for fc in feature_classes:
    print(fc)

# Output Coordinate System environment is different from the input coordinate system,
# the input is projected to the output coordinate system during tool operation.
#This projection will not affect the input
# set coordinate system of output data:
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("USA Contiguous Albers Equal Area Conic USGS")

# ----- START OF ANALYSIS ----- # 

# print current date and time
dt = datetime.datetime.now()
print ("Current date and time:",dt.strftime("%Y-%m-%d %H:%M:%S"),'\n\n')

# set start time for total execution time calculation
start_time_total = time.time()

###############################################################################
# General Overview of Analysis Steps:                                         
###############################################################################

# Step 1. Retreive raw Highway Performance Monitoring System (HPMS) Data. 
# Step 2. Merge all HPMS data into shapefile with all function classifications.
#      >> arcpy.management.Merge()
# Step 3. Check and fix geometry problems.
#      >>  arcpy.conversion.ExportFeatures()
#      >>  arcpy.management.RepairGeometry()
# Step 4. Subset geometry and project data.
#      >> arcpy.conversion.ExportFeatures()
#      >> arcpy.management.Project()
# Step 5. Intersect HPMS road network with County boundaries
#      >> arcpy.analysis.PairwiseIntersect()
# Step 6. Correct urban codes in HPMS data (including links with no urban code)
#      >> arcpy.analysis.SpatialJoin()

###############################################################################


### 2: Merge hpms_2018_fsys123_2019_10_21 and hpms_2018_fsys123_2019_10_21 to HPMS_2018_123456
try:
    arcpy.management.Merge(
        inputs="hpms_2018_fsys123_2019_10_21;hpms_2018_fsys456_2019_10_21",
        output="HPMS_2018_123456",
        field_mappings='Year_Record "Year_Record" true true false 2 Short 0 0,First,#,hpms_2018_fsys123_2019_10_21,Year_Record,-1,-1,hpms_2018_fsys456_2019_10_21,Year_Record,-1,-1;State_Code "State_Code" true true false 2 Short 0 0,First,#,hpms_2018_fsys123_2019_10_21,State_Code,-1,-1,hpms_2018_fsys456_2019_10_21,State_Code,-1,-1;Route_ID "Route_ID" true true false 2048 Text 0 0,First,#,hpms_2018_fsys123_2019_10_21,Route_ID,0,2048,hpms_2018_fsys456_2019_10_21,Route_ID,0,2048;Begin_Point "Begin_Point" true true false 8 Double 0 0,First,#,hpms_2018_fsys123_2019_10_21,Begin_Point,-1,-1,hpms_2018_fsys456_2019_10_21,Begin_Point,-1,-1;End_Point "End_Point" true true false 8 Double 0 0,First,#,hpms_2018_fsys123_2019_10_21,End_Point,-1,-1,hpms_2018_fsys456_2019_10_21,End_Point,-1,-1;AADT "AADT" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,AADT,-1,-1,hpms_2018_fsys456_2019_10_21,AADT,-1,-1;AADT_COMBINATION "AADT_COMBINATION" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,AADT_COMBINATION,-1,-1,hpms_2018_fsys456_2019_10_21,AADT_COMBINATION,-1,-1;AADT_SINGLE_UNIT "AADT_SINGLE_UNIT" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,AADT_SINGLE_UNIT,-1,-1,hpms_2018_fsys456_2019_10_21,AADT_SINGLE_UNIT,-1,-1;ACCESS_CONTROL_ "ACCESS_CONTROL_" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,ACCESS_CONTROL_,-1,-1,hpms_2018_fsys456_2019_10_21,ACCESS_CONTROL_,-1,-1;COUNTY_CODE "COUNTY_CODE" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,COUNTY_CODE,-1,-1,hpms_2018_fsys456_2019_10_21,COUNTY_CODE,-1,-1;F_SYSTEM "F_SYSTEM" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,F_SYSTEM,-1,-1,hpms_2018_fsys456_2019_10_21,F_SYSTEM,-1,-1;FACILITY_TYPE "FACILITY_TYPE" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,FACILITY_TYPE,-1,-1,hpms_2018_fsys456_2019_10_21,FACILITY_TYPE,-1,-1;IRI "IRI" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,IRI,-1,-1,hpms_2018_fsys456_2019_10_21,IRI,-1,-1;IRI_YEAR "IRI_YEAR" true true false 8 Date 0 0,First,#,hpms_2018_fsys123_2019_10_21,IRI_YEAR,-1,-1,hpms_2018_fsys456_2019_10_21,IRI_YEAR,-1,-1;NHS "NHS" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,NHS,-1,-1,hpms_2018_fsys456_2019_10_21,NHS,-1,-1;OWNERSHIP "OWNERSHIP" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,OWNERSHIP,-1,-1,hpms_2018_fsys456_2019_10_21,OWNERSHIP,-1,-1;PSR "PSR" true true false 8 Double 0 0,First,#,hpms_2018_fsys123_2019_10_21,PSR,-1,-1,hpms_2018_fsys456_2019_10_21,PSR,-1,-1;ROUTE_NUMBER "ROUTE_NUMBER" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,ROUTE_NUMBER,-1,-1,hpms_2018_fsys456_2019_10_21,ROUTE_NUMBER,-1,-1;ROUTE_NAME "ROUTE_NAME" true true false 100 Text 0 0,First,#,hpms_2018_fsys123_2019_10_21,ROUTE_NAME,0,100,hpms_2018_fsys456_2019_10_21,ROUTE_NAME,0,100;ROUTE_QUALIFIER "ROUTE_QUALIFIER" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,ROUTE_QUALIFIER,-1,-1,hpms_2018_fsys456_2019_10_21,ROUTE_QUALIFIER,-1,-1;ROUTE_SIGNING "ROUTE_SIGNING" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,ROUTE_SIGNING,-1,-1,hpms_2018_fsys456_2019_10_21,ROUTE_SIGNING,-1,-1;SPEED_LIMIT "SPEED_LIMIT" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,SPEED_LIMIT,-1,-1,hpms_2018_fsys456_2019_10_21,SPEED_LIMIT,-1,-1;STRAHNET_TYPE "STRAHNET_TYPE" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,STRAHNET_TYPE,-1,-1,hpms_2018_fsys456_2019_10_21,STRAHNET_TYPE,-1,-1;STRUCTURE_TYPE "STRUCTURE_TYPE" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,STRUCTURE_TYPE,-1,-1,hpms_2018_fsys456_2019_10_21,STRUCTURE_TYPE,-1,-1;SURFACE_TYPE "SURFACE_TYPE" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,SURFACE_TYPE,-1,-1,hpms_2018_fsys456_2019_10_21,SURFACE_TYPE,-1,-1;THROUGH_LANES "THROUGH_LANES" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,THROUGH_LANES,-1,-1,hpms_2018_fsys456_2019_10_21,THROUGH_LANES,-1,-1;TOLL_CHARGED "TOLL_CHARGED" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,TOLL_CHARGED,-1,-1,hpms_2018_fsys456_2019_10_21,TOLL_CHARGED,-1,-1;TOLL_TYPE "TOLL_TYPE" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,TOLL_TYPE,-1,-1,hpms_2018_fsys456_2019_10_21,TOLL_TYPE,-1,-1;TRUCK "TRUCK" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,TRUCK,-1,-1,hpms_2018_fsys456_2019_10_21,TRUCK,-1,-1;URBAN_CODE "URBAN_CODE" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,URBAN_CODE,-1,-1,hpms_2018_fsys456_2019_10_21,URBAN_CODE,-1,-1;SHAPE_Length "SHAPE_Length" false true true 8 Double 0 0,First,#,hpms_2018_fsys123_2019_10_21,SHAPE_Length,-1,-1,hpms_2018_fsys456_2019_10_21,SHAPE_Length,-1,-1',
        add_source="NO_SOURCE_INFO"
    )
    print('Merged HPMS raw data files to single feature class.')

except Exception as e:
                # print error messages
                print(arcpy.GetMessages())
                print("ERROR: ")
                print(e)
                sys.exit('Exiting script.')

### 3: Repaired geometry and deleted features with Null geometry using ArcGIS ‘Repair Geometry’ geoprocessing tool (Esri method).
try: 
    arcpy.conversion.ExportFeatures(
        in_features="HPMS_2018_123456",
        out_features="HPMS_2018_repair_geo",
     where_clause="",
        use_field_alias_as_name="NOT_USE_ALIAS",
     field_mapping=r'Year_Record "Year_Record" true true false 2 Short 0 0,First,#,HPMS_2018_123456,Year_Record,-1,-1;State_Code "State_Code" true true false 2 Short 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,State_Code,-1,-1;Route_ID "Route_ID" true true false 2048 Text 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,Route_ID,0,2048;Begin_Point "Begin_Point" true true false 8 Double 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,Begin_Point,-1,-1;End_Point "End_Point" true true false 8 Double 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,End_Point,-1,-1;AADT "AADT" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,AADT,-1,-1;AADT_COMBINATION "AADT_COMBINATION" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,AADT_COMBINATION,-1,-1;AADT_SINGLE_UNIT "AADT_SINGLE_UNIT" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,AADT_SINGLE_UNIT,-1,-1;ACCESS_CONTROL_ "ACCESS_CONTROL_" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,ACCESS_CONTROL_,-1,-1;COUNTY_CODE "COUNTY_CODE" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,COUNTY_CODE,-1,-1;F_SYSTEM "F_SYSTEM" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,F_SYSTEM,-1,-1;FACILITY_TYPE "FACILITY_TYPE" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,FACILITY_TYPE,-1,-1;IRI "IRI" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,IRI,-1,-1;IRI_YEAR "IRI_YEAR" true true false 8 Date 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,IRI_YEAR,-1,-1;NHS "NHS" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,NHS,-1,-1;OWNERSHIP "OWNERSHIP" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,OWNERSHIP,-1,-1;PSR "PSR" true true false 8 Double 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,PSR,-1,-1;ROUTE_NUMBER "ROUTE_NUMBER" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,ROUTE_NUMBER,-1,-1;ROUTE_NAME "ROUTE_NAME" true true false 100 Text 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,ROUTE_NAME,0,100;ROUTE_QUALIFIER "ROUTE_QUALIFIER" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,ROUTE_QUALIFIER,-1,-1;ROUTE_SIGNING "ROUTE_SIGNING" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,ROUTE_SIGNING,-1,-1;SPEED_LIMIT "SPEED_LIMIT" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,SPEED_LIMIT,-1,-1;STRAHNET_TYPE "STRAHNET_TYPE" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,STRAHNET_TYPE,-1,-1;STRUCTURE_TYPE "STRUCTURE_TYPE" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,STRUCTURE_TYPE,-1,-1;SURFACE_TYPE "SURFACE_TYPE" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,SURFACE_TYPE,-1,-1;THROUGH_LANES "THROUGH_LANES" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,THROUGH_LANES,-1,-1;TOLL_CHARGED "TOLL_CHARGED" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,TOLL_CHARGED,-1,-1;TOLL_TYPE "TOLL_TYPE" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,TOLL_TYPE,-1,-1;TRUCK "TRUCK" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,TRUCK,-1,-1;URBAN_CODE "URBAN_CODE" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,URBAN_CODE,-1,-1;Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,Shape_Length,-1,-1',
     sort_field=None
    )
    print('Exported full HPMS data to new feature class for cleaning.')

    arcpy.management.RepairGeometry(
     in_features="HPMS_2018_repair_geo",
        delete_null="DELETE_NULL",
        validation_method="ESRI"
    )
    print('Repaired geometry and deleted NULL geometry.')

except Exception as e:
                # print error messages
                print(arcpy.GetMessages())
                print("ERROR: ")
                print(e)
                sys.exit('Exiting script.')

### 4: Subset geometry and project data
try:
    # Extract the feature class name and create a layer name
    fc_name = "HPMS_2018_repair_geo"
    feature_layer_name = "HPMS_2018_state"
    arcpy.MakeFeatureLayer_management(fc_name, feature_layer_name)
    print("Feature layer made from repaired geometry for subsetting.")
    # Select all geometries within the 50 states and DC (Not State_Code = 78 (Virgin Islands) OR 72 (Puerto Rico))
    arcpy.management.SelectLayerByAttribute(in_layer_or_view="HPMS_2018_state", selection_type="NEW_SELECTION",
                                        where_clause="State_Code <> 78 And State_Code <> 72",invert_where_clause=None
    )
    print('Selected geometry inside of 50 states and DC.')
    arcpy.management.CopyFeatures(in_features="HPMS_2018_state", out_feature_class= "HPMS_2018_state_sub_proj"
    )
    print("Feature layer copied to state subset feature class.")


    # Project HPMS data into "USA Contiguous Albers Equal Area Conic USGS"
    # This is not performed as a seperate tools when output coordinate system is defined in user-defined variables

except Exception as e:
                # print error messages
                print(arcpy.GetMessages())
                print("ERROR: ")
                print(e)
                sys.exit('Exiting script.')


### 5: Intersect HPMS road network with US Census county boundaries
try:
    arcpy.analysis.PairwiseIntersect(
        in_features="HPMS_2018_state_sub_proj;US_census_county_2020",
        out_feature_class="HPMS_2018_county_intxn",
        join_attributes="ALL",
        cluster_tolerance=None,
        output_type="INPUT"
    )
    print('Intersected HPMS state subset with US census counties.')

except Exception as e:
                # print error messages
                print(arcpy.GetMessages())
                print("ERROR: ")
                print(e)
                sys.exit('Exiting script.')

# Calculate new field for road link FID: [FID_Link_Cnty_Intxn]
try:
    # create new field
    inFeatures = "HPMS_2018_county_intxn"
    fieldName = "FID_Link_Cnty_Intxn"
    arcpy.management.AddField(inFeatures, fieldName, "LONG")
    arcpy.management.CalculateField(inFeatures, fieldName, "!FID_HPMS_2018_state_sub_proj!", "PYTHON3")
    print('Calculated new field for road link FID: [FID_Link_Cnty_Intxn]')

except Exception as e:
                # print error messages
                print(arcpy.GetMessages())
                print("ERROR: ")
                print(e)
                sys.exit('Exiting script.')

### 6: Correct urban codes in HPMS data 
try:
    arcpy.analysis.SpatialJoin(
        target_features="HPMS_2018_county_intxn",
        join_features="US_census_uac_2010",
        out_feature_class="HPMS_2018_cnty_uac_join",
        join_operation="JOIN_ONE_TO_ONE",
        join_type="KEEP_ALL",
        field_mapping='FID_HPMS_2018_state_sub_proj "FID_HPMS_2018_state_sub_proj" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,FID_HPMS_2018_state_sub_proj,-1,-1;Year_Record "Year_Record" true true false 2 Short 0 0,First,#,HPMS_2018_county_intxn,Year_Record,-1,-1;State_Code "State_Code" true true false 2 Short 0 0,First,#,HPMS_2018_county_intxn,State_Code,-1,-1;Route_ID "Route_ID" true true false 2048 Text 0 0,First,#,HPMS_2018_county_intxn,Route_ID,0,2048;Begin_Point "Begin_Point" true true false 8 Double 0 0,First,#,HPMS_2018_county_intxn,Begin_Point,-1,-1;End_Point "End_Point" true true false 8 Double 0 0,First,#,HPMS_2018_county_intxn,End_Point,-1,-1;AADT "AADT" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,AADT,-1,-1;AADT_COMBINATION "AADT_COMBINATION" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,AADT_COMBINATION,-1,-1;AADT_SINGLE_UNIT "AADT_SINGLE_UNIT" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,AADT_SINGLE_UNIT,-1,-1;ACCESS_CONTROL_ "ACCESS_CONTROL_" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,ACCESS_CONTROL_,-1,-1;COUNTY_CODE "COUNTY_CODE" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,COUNTY_CODE,-1,-1;F_SYSTEM "F_SYSTEM" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,F_SYSTEM,-1,-1;FACILITY_TYPE "FACILITY_TYPE" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,FACILITY_TYPE,-1,-1;IRI "IRI" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,IRI,-1,-1;IRI_YEAR "IRI_YEAR" true true false 8 Date 0 0,First,#,HPMS_2018_county_intxn,IRI_YEAR,-1,-1;NHS "NHS" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,NHS,-1,-1;OWNERSHIP "OWNERSHIP" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,OWNERSHIP,-1,-1;PSR "PSR" true true false 8 Double 0 0,First,#,HPMS_2018_county_intxn,PSR,-1,-1;ROUTE_NUMBER "ROUTE_NUMBER" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,ROUTE_NUMBER,-1,-1;ROUTE_NAME "ROUTE_NAME" true true false 100 Text 0 0,First,#,HPMS_2018_county_intxn,ROUTE_NAME,0,100;ROUTE_QUALIFIER "ROUTE_QUALIFIER" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,ROUTE_QUALIFIER,-1,-1;ROUTE_SIGNING "ROUTE_SIGNING" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,ROUTE_SIGNING,-1,-1;SPEED_LIMIT "SPEED_LIMIT" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,SPEED_LIMIT,-1,-1;STRAHNET_TYPE "STRAHNET_TYPE" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,STRAHNET_TYPE,-1,-1;STRUCTURE_TYPE "STRUCTURE_TYPE" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,STRUCTURE_TYPE,-1,-1;SURFACE_TYPE "SURFACE_TYPE" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,SURFACE_TYPE,-1,-1;THROUGH_LANES "THROUGH_LANES" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,THROUGH_LANES,-1,-1;TOLL_CHARGED "TOLL_CHARGED" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,TOLL_CHARGED,-1,-1;TOLL_TYPE "TOLL_TYPE" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,TOLL_TYPE,-1,-1;TRUCK "TRUCK" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,TRUCK,-1,-1;URBAN_CODE "URBAN_CODE" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,URBAN_CODE,-1,-1;FID_US_census_county_2020 "FID_US_census_county_2020" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,FID_US_census_county_2020,-1,-1;STATEFP "STATEFP" true true false 2 Text 0 0,First,#,HPMS_2018_county_intxn,STATEFP,0,2;COUNTYFP "COUNTYFP" true true false 3 Text 0 0,First,#,HPMS_2018_county_intxn,COUNTYFP,0,3;COUNTYNS "COUNTYNS" true true false 8 Text 0 0,First,#,HPMS_2018_county_intxn,COUNTYNS,0,8;GEOID "GEOID" true true false 5 Text 0 0,First,#,HPMS_2018_county_intxn,GEOID,0,5;NAME "NAME" true true false 100 Text 0 0,First,#,HPMS_2018_county_intxn,NAME,0,100;NAMELSAD "NAMELSAD" true true false 100 Text 0 0,First,#,HPMS_2018_county_intxn,NAMELSAD,0,100;Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,HPMS_2018_county_intxn,Shape_Length,-1,-1;FID_Link_Cnty_Intxn "FID_Link_Cnty_Intxn" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,FID_Link_Cnty_Intxn,-1,-1;UACE10 "UACE10" true true false 5 Text 0 0,First,#,US_census_uac_2010,UACE10,0,5;GEOID10 "GEOID10" true true false 5 Text 0 0,First,#,US_census_uac_2010,GEOID10,0,5;NAME10 "NAME10" true true false 100 Text 0 0,First,#,US_census_uac_2010,NAME10,0,100;NAMELSAD10 "NAMELSAD10" true true false 100 Text 0 0,First,#,US_census_uac_2010,NAMELSAD10,0,100;UATYP10 "UATYP10" true true false 1 Text 0 0,First,#,US_census_uac_2010,UATYP10,0,1;Shape_Length_1 "Shape_Length" false true true 8 Double 0 0,First,#,US_census_uac_2010,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0,First,#,US_census_uac_2010,Shape_Area,-1,-1',
        match_option="HAVE_THEIR_CENTER_IN",
        search_radius=None,
        distance_field_name=""
    )
    print('Spatially joined HPMS road network with US Census urban areas.')

except Exception as e:
                # print error messages
                print(arcpy.GetMessages())
                print("ERROR: ")
                print(e)
                sys.exit('Exiting script.')

# print total execution time calculation 
print('Total Execution time: --- %s hours ---\n' % round(((time.time() - start_time_total)*(1/(60*60)))))

# ----- END OF SCRIPT ----- #
print('----- END OF SCRIPT -----')
