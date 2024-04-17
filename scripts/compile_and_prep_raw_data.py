"""
HPMS Data Paper
by Aviral Chawla, Meg Fay, and Britanny Antonczak

Summary: This script 
1) Creates two file geodatabases for storing processed data,
2) Compiles the raw data into two file geodatabases for analysis, 
3) Cleans and merges the HPMS network, intersects HPMS links with US county census boundaries, and adds rural-urban codes to road links in the network.

<LICENSE>
"""
# import statements
import arcpy
import os
import sys
from pathlib import Path

# overwrite existing files (False = No, True = Yes)
arcpy.env.overwriteOutput = True
print('arcpy.env.overwriteOutput', arcpy.env.overwriteOutput,'\n')

# --- FILE GDB CREATION  ---

# Prepare storage directory
STORAGE_DIR = Path("../data/processed_data")
if not STORAGE_DIR.exists():
    STORAGE_DIR.mkdir(parents=True)

# Create file geodatabase for HPMS data
gdb_folder_path = STORAGE_DIR / "HPMS"
gdb_name = "HPMS.gdb"
arcpy.CreateFileGDB_management(gdb_folder_path, gdb_name)
HPMS_gdb = os.path.join(gdb_folder_path, gdb_name)
print(f"Created file geodatabase for HPMS data: {HPMS_gdb}")

# Create file geodatabase for Traffic Density data
gdb_folder_path = STORAGE_DIR / "Traffic_Density"
gdb_name = "Traffic_Density.gdb"
arcpy.CreateFileGDB_management(gdb_folder_path, gdb_name)
Traffic_Density_gdb = os.path.join(gdb_folder_path, gdb_name)
print(f"Created file geodatabase for Traffic Density data: {Traffic_Density_gdb}")

# --- DATA COMPILE ---

# Compile all raw data needed for HPMS analysis
arcpy.env.workspace = HPMS_gdb

print("Copying raw HPMS data to HPMS file geodatabase...")

HPMS_raw_gdb = "../data/raw_data/ntad_2019_hpms_raw/NTAD2019_GDB_HPMS2018_2019_10_21.gdb"
fc_123 = "hpms_2018_fsys123_2019_10_21"
fc_456 = "hpms_2018_fsys456_2019_10_21"
arcpy.Copy_management(f"{HPMS_raw_gdb}\\{fc_123}", f"{HPMS_gdb}\\{fc_123}")
arcpy.Copy_management(f"{HPMS_raw_gdb}\\{fc_456}", f"{HPMS_gdb}\\{fc_456}")

print("Copied raw HPMS data to HPMS file geodatabase.")

print("Exporting raw Census county data to HPMS file geodatabase...")

in_features = "../data/raw_data/census/counties/tl_2020_us_county/tl_2020_us_county.shp"
out_features = f"{HPMS_gdb}\\US_census_county_2020"
where_clause = ""
use_field_alias_as_name = "NOT_USE_ALIAS"
arcpy.conversion.ExportFeatures(in_features, out_features, where_clause, use_field_alias_as_name)

print("Exported raw Census county data to HPMS file geodatabase.")

print("Exporting raw Census urban area data to HPMS file geodatabase...")

in_features = "../data/raw_data/census/urban_areas/tl_2020_us_uac10/tl_2020_us_uac10.shp"
out_features = f"{HPMS_gdb}\\US_census_uac_2010"
where_clause = ""
use_field_alias_as_name = "NOT_USE_ALIAS"
arcpy.conversion.ExportFeatures(in_features, out_features, where_clause, use_field_alias_as_name)

print("Exported raw Census urban area data to HPMS file geodatabase.")

# Compile all raw data needed for Traffic Density analysis
arcpy.env.workspace = Traffic_Density_gdb

print("Exporting raw Census blocks data to Traffic Density file geodatabase...")

state_fips_codes = ['01', '02', '04', '05', '06', '08', '09', '10', '11', '12', '13', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '44', '45', '46', '47', '48', '49', '50', '51', '53', '54', '55', '56', '60', '66', '69', '72', '78']
base_file_path = "../data/raw_data/census/blocks/tl_2020_{}_tabblock10/tl_2020_{}_tabblock10.shp"
file_paths = [base_file_path.format(fips) for fips in state_fips_codes]

for file_path in file_paths:
    out_feature_class = f"{Traffic_Density_gdb}\\{os.path.basename(file_path).split('.')[0]}"
    arcpy.conversion.FeatureClassToFeatureClass(file_path, Traffic_Density_gdb, out_feature_class)

print("Exported raw Census blocks data to Traffic Density file geodatabase.")

# --- HPMS Data Preparation ---

# Set the workspace
# The default location for geoprocessing tool input and output
arcpy.env.workspace = "../data/processed_data/HPMS/HPMS.gdb"

# Output Coordinate System environment is different from the input coordinate system,
# the input is projected to the output coordinate system during tool operation.
#This projection will not affect the input
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("USA Contiguous Albers Equal Area Conic USGS")
# If verifying results using ArcGIS GUI -> check basemap
# Coordinate System "USA Contiguous Albers Equal Area Conic USGS"

# merge HPMS data
inputs = "hpms_2018_fsys123_2019_10_21;hpms_2018_fsys456_2019_10_21"
output = "HPMS_2018_123456"
field_mappings='Year_Record "Year_Record" true true false 2 Short 0 0,First,#,hpms_2018_fsys123_2019_10_21,Year_Record,-1,-1,hpms_2018_fsys456_2019_10_21,Year_Record,-1,-1;State_Code "State_Code" true true false 2 Short 0 0,First,#,hpms_2018_fsys123_2019_10_21,State_Code,-1,-1,hpms_2018_fsys456_2019_10_21,State_Code,-1,-1;Route_ID "Route_ID" true true false 2048 Text 0 0,First,#,hpms_2018_fsys123_2019_10_21,Route_ID,0,2048,hpms_2018_fsys456_2019_10_21,Route_ID,0,2048;Begin_Point "Begin_Point" true true false 8 Double 0 0,First,#,hpms_2018_fsys123_2019_10_21,Begin_Point,-1,-1,hpms_2018_fsys456_2019_10_21,Begin_Point,-1,-1;End_Point "End_Point" true true false 8 Double 0 0,First,#,hpms_2018_fsys123_2019_10_21,End_Point,-1,-1,hpms_2018_fsys456_2019_10_21,End_Point,-1,-1;AADT "AADT" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,AADT,-1,-1,hpms_2018_fsys456_2019_10_21,AADT,-1,-1;AADT_COMBINATION "AADT_COMBINATION" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,AADT_COMBINATION,-1,-1,hpms_2018_fsys456_2019_10_21,AADT_COMBINATION,-1,-1;AADT_SINGLE_UNIT "AADT_SINGLE_UNIT" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,AADT_SINGLE_UNIT,-1,-1,hpms_2018_fsys456_2019_10_21,AADT_SINGLE_UNIT,-1,-1;ACCESS_CONTROL_ "ACCESS_CONTROL_" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,ACCESS_CONTROL_,-1,-1,hpms_2018_fsys456_2019_10_21,ACCESS_CONTROL_,-1,-1;COUNTY_CODE "COUNTY_CODE" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,COUNTY_CODE,-1,-1,hpms_2018_fsys456_2019_10_21,COUNTY_CODE,-1,-1;F_SYSTEM "F_SYSTEM" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,F_SYSTEM,-1,-1,hpms_2018_fsys456_2019_10_21,F_SYSTEM,-1,-1;FACILITY_TYPE "FACILITY_TYPE" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,FACILITY_TYPE,-1,-1,hpms_2018_fsys456_2019_10_21,FACILITY_TYPE,-1,-1;IRI "IRI" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,IRI,-1,-1,hpms_2018_fsys456_2019_10_21,IRI,-1,-1;IRI_YEAR "IRI_YEAR" true true false 8 Date 0 0,First,#,hpms_2018_fsys123_2019_10_21,IRI_YEAR,-1,-1,hpms_2018_fsys456_2019_10_21,IRI_YEAR,-1,-1;NHS "NHS" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,NHS,-1,-1,hpms_2018_fsys456_2019_10_21,NHS,-1,-1;OWNERSHIP "OWNERSHIP" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,OWNERSHIP,-1,-1,hpms_2018_fsys456_2019_10_21,OWNERSHIP,-1,-1;PSR "PSR" true true false 8 Double 0 0,First,#,hpms_2018_fsys123_2019_10_21,PSR,-1,-1,hpms_2018_fsys456_2019_10_21,PSR,-1,-1;ROUTE_NUMBER "ROUTE_NUMBER" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,ROUTE_NUMBER,-1,-1,hpms_2018_fsys456_2019_10_21,ROUTE_NUMBER,-1,-1;ROUTE_NAME "ROUTE_NAME" true true false 100 Text 0 0,First,#,hpms_2018_fsys123_2019_10_21,ROUTE_NAME,0,100,hpms_2018_fsys456_2019_10_21,ROUTE_NAME,0,100;ROUTE_QUALIFIER "ROUTE_QUALIFIER" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,ROUTE_QUALIFIER,-1,-1,hpms_2018_fsys456_2019_10_21,ROUTE_QUALIFIER,-1,-1;ROUTE_SIGNING "ROUTE_SIGNING" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,ROUTE_SIGNING,-1,-1,hpms_2018_fsys456_2019_10_21,ROUTE_SIGNING,-1,-1;SPEED_LIMIT "SPEED_LIMIT" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,SPEED_LIMIT,-1,-1,hpms_2018_fsys456_2019_10_21,SPEED_LIMIT,-1,-1;STRAHNET_TYPE "STRAHNET_TYPE" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,STRAHNET_TYPE,-1,-1,hpms_2018_fsys456_2019_10_21,STRAHNET_TYPE,-1,-1;STRUCTURE_TYPE "STRUCTURE_TYPE" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,STRUCTURE_TYPE,-1,-1,hpms_2018_fsys456_2019_10_21,STRUCTURE_TYPE,-1,-1;SURFACE_TYPE "SURFACE_TYPE" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,SURFACE_TYPE,-1,-1,hpms_2018_fsys456_2019_10_21,SURFACE_TYPE,-1,-1;THROUGH_LANES "THROUGH_LANES" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,THROUGH_LANES,-1,-1,hpms_2018_fsys456_2019_10_21,THROUGH_LANES,-1,-1;TOLL_CHARGED "TOLL_CHARGED" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,TOLL_CHARGED,-1,-1,hpms_2018_fsys456_2019_10_21,TOLL_CHARGED,-1,-1;TOLL_TYPE "TOLL_TYPE" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,TOLL_TYPE,-1,-1,hpms_2018_fsys456_2019_10_21,TOLL_TYPE,-1,-1;TRUCK "TRUCK" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,TRUCK,-1,-1,hpms_2018_fsys456_2019_10_21,TRUCK,-1,-1;URBAN_CODE "URBAN_CODE" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,URBAN_CODE,-1,-1,hpms_2018_fsys456_2019_10_21,URBAN_CODE,-1,-1;SHAPE_Length "SHAPE_Length" false true true 8 Double 0 0,First,#,hpms_2018_fsys123_2019_10_21,SHAPE_Length,-1,-1,hpms_2018_fsys456_2019_10_21,SHAPE_Length,-1,-1',
add_source = "NO_SOURCE_INFO"
arcpy.management.Merge(inputs, output, field_mappings, add_source)
print('Merged HPMS raw data files to single feature class.')

# repair geometry
in_features = "HPMS_2018_123456"
out_features = "HPMS_2018_repair_geo"
where_clause = ""
use_field_alias_as_name = "NOT_USE_ALIAS"
field_mapping=r'Year_Record "Year_Record" true true false 2 Short 0 0,First,#,HPMS_2018_123456,Year_Record,-1,-1;State_Code "State_Code" true true false 2 Short 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,State_Code,-1,-1;Route_ID "Route_ID" true true false 2048 Text 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,Route_ID,0,2048;Begin_Point "Begin_Point" true true false 8 Double 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,Begin_Point,-1,-1;End_Point "End_Point" true true false 8 Double 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,End_Point,-1,-1;AADT "AADT" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,AADT,-1,-1;AADT_COMBINATION "AADT_COMBINATION" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,AADT_COMBINATION,-1,-1;AADT_SINGLE_UNIT "AADT_SINGLE_UNIT" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,AADT_SINGLE_UNIT,-1,-1;ACCESS_CONTROL_ "ACCESS_CONTROL_" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,ACCESS_CONTROL_,-1,-1;COUNTY_CODE "COUNTY_CODE" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,COUNTY_CODE,-1,-1;F_SYSTEM "F_SYSTEM" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,F_SYSTEM,-1,-1;FACILITY_TYPE "FACILITY_TYPE" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,FACILITY_TYPE,-1,-1;IRI "IRI" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,IRI,-1,-1;IRI_YEAR "IRI_YEAR" true true false 8 Date 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,IRI_YEAR,-1,-1;NHS "NHS" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,NHS,-1,-1;OWNERSHIP "OWNERSHIP" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,OWNERSHIP,-1,-1;PSR "PSR" true true false 8 Double 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,PSR,-1,-1;ROUTE_NUMBER "ROUTE_NUMBER" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,ROUTE_NUMBER,-1,-1;ROUTE_NAME "ROUTE_NAME" true true false 100 Text 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,ROUTE_NAME,0,100;ROUTE_QUALIFIER "ROUTE_QUALIFIER" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,ROUTE_QUALIFIER,-1,-1;ROUTE_SIGNING "ROUTE_SIGNING" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,ROUTE_SIGNING,-1,-1;SPEED_LIMIT "SPEED_LIMIT" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,SPEED_LIMIT,-1,-1;STRAHNET_TYPE "STRAHNET_TYPE" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,STRAHNET_TYPE,-1,-1;STRUCTURE_TYPE "STRUCTURE_TYPE" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,STRUCTURE_TYPE,-1,-1;SURFACE_TYPE "SURFACE_TYPE" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,SURFACE_TYPE,-1,-1;THROUGH_LANES "THROUGH_LANES" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,THROUGH_LANES,-1,-1;TOLL_CHARGED "TOLL_CHARGED" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,TOLL_CHARGED,-1,-1;TOLL_TYPE "TOLL_TYPE" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,TOLL_TYPE,-1,-1;TRUCK "TRUCK" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,TRUCK,-1,-1;URBAN_CODE "URBAN_CODE" true true false 4 Long 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,URBAN_CODE,-1,-1;Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,Z:\ROAD_AQ\HPMS Traffic Data\HPMS\HPMS.gdb\HPMS_2018_123456,Shape_Length,-1,-1',
sort_field = None
arcpy.conversion.ExportFeatures(in_features, out_features, where_clause, use_field_alias_as_name, field_mapping, sort_field)

in_features = "HPMS_2018_repair_geo"
delete_null = "DELETE_NULL"
validation_method = "ESRI"
arcpy.management.RepairGeometry(in_features, delete_null, validation_method)
print('Repaired geometry of HPMS road network.')

# subset geometry to 50 states and Washington DC
fc_name = "HPMS_2018_repair_geo"
feature_layer_name = "HPMS_2018_state"
arcpy.management.MakeFeatureLayer(fc_name, feature_layer_name)

in_layer_or_view = "HPMS_2018_state"
selection_type = "NEW_SELECTION"
where_clause = "State_Code <> 78 And State_Code <> 72"
invert_where_clause = None
arcpy.management.SelectLayerByAttribute(in_layer_or_view, selection_type, where_clause, invert_where_clause)

in_features = "HPMS_2018_state"
out_feature_class = "HPMS_2018_state_sub_proj"
arcpy.management.CopyFeatures(in_features, out_feature_class)
print('Subsetted HPMS road network to 50 states and Washington DC.')

# intersect HPMS road network with US county boundaries
in_features="HPMS_2018_state_sub_proj;US_census_county_2020",
out_feature_class="HPMS_2018_county_intxn",
join_attributes="ALL",
cluster_tolerance=None,
output_type="INPUT"
arcpy.analysis.PairwiseIntersect(in_features, out_feature_class, join_attributes, cluster_tolerance, output_type)
print('Intersected HPMS road network with US county boundaries.')

# generate new field with unique ID 
inFeatures = "HPMS_2018_county_intxn"
fieldName = "FID_Link_Cnty_Intxn"
arcpy.management.AddField(inFeatures, fieldName, "LONG")
expression = "!OBJECTID!"
expression_type = "PYTHON3"
arcpy.management.CalculateField(inFeatures, fieldName, expression, expression_type)
print('Calculated new field for road link FID: [FID_Link_Cnty_Intxn]')

# correct urban codes in HPMS data (including links with no urban code)
target_features = ""
join_features = ""
out_feature_class = ""
join_operation = "JOIN_ONE_TO_ONE"
join_type = "KEEP_ALL"
field_mapping='FID_HPMS_2018_state_sub_proj "FID_HPMS_2018_state_sub_proj" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,FID_HPMS_2018_state_sub_proj,-1,-1;Year_Record "Year_Record" true true false 2 Short 0 0,First,#,HPMS_2018_county_intxn,Year_Record,-1,-1;State_Code "State_Code" true true false 2 Short 0 0,First,#,HPMS_2018_county_intxn,State_Code,-1,-1;Route_ID "Route_ID" true true false 2048 Text 0 0,First,#,HPMS_2018_county_intxn,Route_ID,0,2048;Begin_Point "Begin_Point" true true false 8 Double 0 0,First,#,HPMS_2018_county_intxn,Begin_Point,-1,-1;End_Point "End_Point" true true false 8 Double 0 0,First,#,HPMS_2018_county_intxn,End_Point,-1,-1;AADT "AADT" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,AADT,-1,-1;AADT_COMBINATION "AADT_COMBINATION" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,AADT_COMBINATION,-1,-1;AADT_SINGLE_UNIT "AADT_SINGLE_UNIT" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,AADT_SINGLE_UNIT,-1,-1;ACCESS_CONTROL_ "ACCESS_CONTROL_" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,ACCESS_CONTROL_,-1,-1;COUNTY_CODE "COUNTY_CODE" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,COUNTY_CODE,-1,-1;F_SYSTEM "F_SYSTEM" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,F_SYSTEM,-1,-1;FACILITY_TYPE "FACILITY_TYPE" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,FACILITY_TYPE,-1,-1;IRI "IRI" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,IRI,-1,-1;IRI_YEAR "IRI_YEAR" true true false 8 Date 0 0,First,#,HPMS_2018_county_intxn,IRI_YEAR,-1,-1;NHS "NHS" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,NHS,-1,-1;OWNERSHIP "OWNERSHIP" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,OWNERSHIP,-1,-1;PSR "PSR" true true false 8 Double 0 0,First,#,HPMS_2018_county_intxn,PSR,-1,-1;ROUTE_NUMBER "ROUTE_NUMBER" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,ROUTE_NUMBER,-1,-1;ROUTE_NAME "ROUTE_NAME" true true false 100 Text 0 0,First,#,HPMS_2018_county_intxn,ROUTE_NAME,0,100;ROUTE_QUALIFIER "ROUTE_QUALIFIER" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,ROUTE_QUALIFIER,-1,-1;ROUTE_SIGNING "ROUTE_SIGNING" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,ROUTE_SIGNING,-1,-1;SPEED_LIMIT "SPEED_LIMIT" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,SPEED_LIMIT,-1,-1;STRAHNET_TYPE "STRAHNET_TYPE" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,STRAHNET_TYPE,-1,-1;STRUCTURE_TYPE "STRUCTURE_TYPE" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,STRUCTURE_TYPE,-1,-1;SURFACE_TYPE "SURFACE_TYPE" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,SURFACE_TYPE,-1,-1;THROUGH_LANES "THROUGH_LANES" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,THROUGH_LANES,-1,-1;TOLL_CHARGED "TOLL_CHARGED" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,TOLL_CHARGED,-1,-1;TOLL_TYPE "TOLL_TYPE" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,TOLL_TYPE,-1,-1;TRUCK "TRUCK" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,TRUCK,-1,-1;URBAN_CODE "URBAN_CODE" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,URBAN_CODE,-1,-1;FID_US_census_county_2020 "FID_US_census_county_2020" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,FID_US_census_county_2020,-1,-1;STATEFP "STATEFP" true true false 2 Text 0 0,First,#,HPMS_2018_county_intxn,STATEFP,0,2;COUNTYFP "COUNTYFP" true true false 3 Text 0 0,First,#,HPMS_2018_county_intxn,COUNTYFP,0,3;COUNTYNS "COUNTYNS" true true false 8 Text 0 0,First,#,HPMS_2018_county_intxn,COUNTYNS,0,8;GEOID "GEOID" true true false 5 Text 0 0,First,#,HPMS_2018_county_intxn,GEOID,0,5;NAME "NAME" true true false 100 Text 0 0,First,#,HPMS_2018_county_intxn,NAME,0,100;NAMELSAD "NAMELSAD" true true false 100 Text 0 0,First,#,HPMS_2018_county_intxn,NAMELSAD,0,100;Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,HPMS_2018_county_intxn,Shape_Length,-1,-1;FID_Link_Cnty_Intxn "FID_Link_Cnty_Intxn" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,FID_Link_Cnty_Intxn,-1,-1;UACE10 "UACE10" true true false 5 Text 0 0,First,#,US_census_uac_2010,UACE10,0,5;GEOID10 "GEOID10" true true false 5 Text 0 0,First,#,US_census_uac_2010,GEOID10,0,5;NAME10 "NAME10" true true false 100 Text 0 0,First,#,US_census_uac_2010,NAME10,0,100;NAMELSAD10 "NAMELSAD10" true true false 100 Text 0 0,First,#,US_census_uac_2010,NAMELSAD10,0,100;UATYP10 "UATYP10" true true false 1 Text 0 0,First,#,US_census_uac_2010,UATYP10,0,1;Shape_Length_1 "Shape_Length" false true true 8 Double 0 0,First,#,US_census_uac_2010,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0,First,#,US_census_uac_2010,Shape_Area,-1,-1',
match_option="HAVE_THEIR_CENTER_IN",
search_radius=None,
distance_field_name=""
arcpy.analysis.SpatialJoin(target_features, join_features, out_feature_class, join_operation, join_type, field_mapping, match_option, search_radius, distance_field_name)
print('Corrected urban codes in HPMS data.')