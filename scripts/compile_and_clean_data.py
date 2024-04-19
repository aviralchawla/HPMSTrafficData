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
try:
    import arcpy
    ARCPY = True
except:
    import geopandas as gpd
    import fiona
    from utils.utilts import shp_to_gdb, get_state_fips
    ARCPY = False
    print('ArcPy is not available. Data will be processed differently')

import os
import sys
from pathlib import Path
import tqdm

class HPMSDataPreparation:
    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        if not storage_dir.exists():
            storage_dir.mkdir(parents=True)
        self.hpms_dir = storage_dir / "HPMS"
        if not self.hpms_dir.exists():
            self.hpms_dir.mkdir(parents=True)
        self.td_dir = storage_dir / "Traffic_Density"
        if not self.td_dir.exists():
            self.td_dir.mkdir(parents=True)
    
        self.hpms_gdb = self.hpms_dir / "HPMS.gdb"
        self.td_gdb = self.td_dir / "Traffic_Density.gdb"

    def copy_raw_hpms(self, hpms_raw_gdb: Path):
        '''
        Summary: Copy raw HPMS data to HPMS file geodatabase in processed data dir
        Inputs:
            - hpms_raw_gdb (Path): Path to the raw HPMS data
        Outputs:
            - hpms (dict): Dictionary of HPMS data layers
        '''

        print("Copying raw HPMS data to HPMS file geodatabase...")

        hpms = {}

        # List all layers in the HPMS raw data
        with fiona.Env():
            hpms_raw_layers = fiona.listlayers(hpms_raw_gdb)

        for layer in tqdm.tqdm(hpms_raw_layers):
            if 'fsys' in layer:
                hpms[layer] = gpd.read_file(hpms_raw_gdb, layer=layer)
                hpms[layer].to_file(self.hpms_gdb, layer=layer, driver='OpenFileGDB')
        
        return hpms
    
    def copy_raw_census(self, census_shp: Path):
        pass

    def copy_raw_census_urban(self, urban_areas_shp: Path):
        pass

    def copy_raw_census_blocks(self, blocks_dir: Path):
        pass

    def merge_hpms_data(self):
        pass

    def repair_hpms_geometry(self):
        pass

    def subset_hpms_geometry(self):
        pass

    def intersect_hpms_county(self):
        pass

    def add_unique_id(self):
        pass

    def correct_urban_codes(self):
        pass
    
class ArcPyHPMSDataPreparation:
    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        if not storage_dir.exists():
            storage_dir.mkdir(parents=True)
        self.hpms_dir = storage_dir / "HPMS"
        if not self.hpms_dir.exists():
            self.hpms_dir.mkdir(parents=True)
        self.td_dir = storage_dir / "Traffic_Density"
        if not self.td_dir.exists():
            self.td_dir.mkdir(parents=True)

        self.hpms_gdb = self.hpms_dir / "HPMS.gdb"
        self.td_gdb = self.td_dir / "Traffic_Density.gdb"

        arcpy.env.overwriteOutput = True
        print('arcpy.env.overwriteOutput', arcpy.env.overwriteOutput,'\n')
    
    def make_hpms_gdb(self):
        gdb_folder_path = str(self.hpms_dir.absolute())
        gdb_name = "HPMS.gdb"
        arcpy.CreateFileGDB_management(gdb_folder_path, gdb_name)
        HPMS_gdb = os.path.join(gdb_folder_path, gdb_name)
        print(f"Created file geodatabase for HPMS data: {HPMS_gdb}")
    
    def make_td_gdb(self):
        gdb_folder_path = str(self.td_dir.absolute())
        gdb_name = "Traffic_Density.gdb"
        arcpy.CreateFileGDB_management(gdb_folder_path, gdb_name)
        Traffic_Density_gdb = os.path.join(gdb_folder_path, gdb_name)
        print(f"Created file geodatabase for Traffic Density data: {Traffic_Density_gdb}")
    
    def copy_raw_hpms(self, hpms_raw_gdb: Path):
        '''
        Summary: Copy raw HPMS data to HPMS file geodatabase in processed data dir using ArcPy
        Inputs:
            - hpm_raw_dir (Path): Path to the raw HPMS data
            - hpms_final_dir (Path): Path to the HPMS file geodatabase
        Outputs:
            - hpms (dict): Dictionary of HPMS data layers
        '''
        self.make_hpms_gdb()

        print("Copying raw HPMS data to HPMS file geodatabase...")

        arcpy.env.workspace = self.hpms_gdb

        fc_123 = "hpms_2018_fsys123_2019_10_21"
        fc_456 = "hpms_2018_fsys456_2019_10_21"

        self.hpms_fc_123 = fc_123
        self.hpms_fc_456 = fc_456

        arcpy.Copy_management(f"{hpms_raw_gdb}\\{fc_123}", f"{hpms_raw_gdb}\\{fc_123}")
        arcpy.Copy_management(f"{hpms_raw_gdb}\\{fc_456}", f"{hpms_raw_gdb}\\{fc_456}")
    
    def copy_raw_census(self, census_shp: Path):
        '''
        Summary: Copy raw Census data to HPMS file geodatabase in processed data dir using ArcPy
        Inputs:
            - census_shp (Path): Path to the raw Census shapefile
        '''
        print("Copying raw Census data to HPMS file geodatabase...")

        arcpy.env.workspace = self.hpms_gdb

        in_features = census_shp.absolute()
        out_features = f'{self.hpms_gdb}\\US_census_county_2020'
        where_clause = ""
        use_field_alias_as_name = "NOT_USE_ALIAS"
        arcpy.conversion.ExportFeatures(in_features, out_features, where_clause, use_field_alias_as_name)
    
    def copy_raw_census_urban(self, urban_areas_shp: Path):
        '''
        Summary: Copy raw Census urban area data to HPMS file geodatabase in processed data dir using ArcPy

        Inputs:
            - urban_areas_shp (Path): Path to the raw Census urban area shapefile
        '''

        print("Copying raw Census urban area data to HPMS file geodatabase...")

        arcpy.env.workspace = self.hpms_gdb

        in_features = urban_areas_shp.absolute()
        out_features = f'{self.hpms_gdb}\\US_census_uac_2010'
        where_clause = ""
        use_field_alias_as_name = "NOT_USE_ALIAS"
        arcpy.conversion.ExportFeatures(in_features, out_features, where_clause, use_field_alias_as_name)
    
    def copy_raw_census_blocks(self, blocks_dir: Path,):
        '''
        Summary: Copy raw Census blocks data to Traffic Density file geodatabase in processed data dir using ArcPy
        Input: 
            - blocks_dir (Path): Path to the raw Census blocks data
        '''
        print("Copying raw Census blocks data to Traffic Density file geodatabase...")
        
        self.make_td_gdb()

        arcpy.env.workspace = self.td_gdb

        state_fips_codes = get_state_fips(blocks_dir)
        base_file_path = "../data/raw_data/census/blocks/tl_2020_{}_tabblock10/tl_2020_{}_tabblock10.shp"

        for fips in tqdm.tqdm(state_fips_codes):
            in_features = base_file_path.format(fips, fips)
            out_features = f"{self.td_gdb}\\{os.path.basename(in_features).split('.')[0]}"
            where_clause = ""
            use_field_alias_as_name = "NOT_USE_ALIAS"
            arcpy.conversion.ExportFeatures(in_features, out_features, where_clause, use_field_alias_as_name)
    
    def merge_hpms_data(self):
        '''
        Summmary: Merge the HPMS data from the two feature classes into a single feature class
        '''
        print("Merging HPMS data...")

        arcpy.env.workspace = self.hpms_gdb
        arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("USA Contiguous Albers Equal Area Conic USGS")

        inputs = f"{self.hpms_fc_123};{self.hpms_fc_456}"
        output = "HPMS_2018_123456"
        self.hpms_fc_123456 = output
        #TODO: Load field mappings from local file!
        field_mappings='Year_Record "Year_Record" true true false 2 Short 0 0,First,#,hpms_2018_fsys123_2019_10_21,Year_Record,-1,-1,hpms_2018_fsys456_2019_10_21,Year_Record,-1,-1;State_Code "State_Code" true true false 2 Short 0 0,First,#,hpms_2018_fsys123_2019_10_21,State_Code,-1,-1,hpms_2018_fsys456_2019_10_21,State_Code,-1,-1;Route_ID "Route_ID" true true false 2048 Text 0 0,First,#,hpms_2018_fsys123_2019_10_21,Route_ID,0,2048,hpms_2018_fsys456_2019_10_21,Route_ID,0,2048;Begin_Point "Begin_Point" true true false 8 Double 0 0,First,#,hpms_2018_fsys123_2019_10_21,Begin_Point,-1,-1,hpms_2018_fsys456_2019_10_21,Begin_Point,-1,-1;End_Point "End_Point" true true false 8 Double 0 0,First,#,hpms_2018_fsys123_2019_10_21,End_Point,-1,-1,hpms_2018_fsys456_2019_10_21,End_Point,-1,-1;AADT "AADT" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,AADT,-1,-1,hpms_2018_fsys456_2019_10_21,AADT,-1,-1;AADT_COMBINATION "AADT_COMBINATION" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,AADT_COMBINATION,-1,-1,hpms_2018_fsys456_2019_10_21,AADT_COMBINATION,-1,-1;AADT_SINGLE_UNIT "AADT_SINGLE_UNIT" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,AADT_SINGLE_UNIT,-1,-1,hpms_2018_fsys456_2019_10_21,AADT_SINGLE_UNIT,-1,-1;ACCESS_CONTROL_ "ACCESS_CONTROL_" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,ACCESS_CONTROL_,-1,-1,hpms_2018_fsys456_2019_10_21,ACCESS_CONTROL_,-1,-1;COUNTY_CODE "COUNTY_CODE" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,COUNTY_CODE,-1,-1,hpms_2018_fsys456_2019_10_21,COUNTY_CODE,-1,-1;F_SYSTEM "F_SYSTEM" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,F_SYSTEM,-1,-1,hpms_2018_fsys456_2019_10_21,F_SYSTEM,-1,-1;FACILITY_TYPE "FACILITY_TYPE" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,FACILITY_TYPE,-1,-1,hpms_2018_fsys456_2019_10_21,FACILITY_TYPE,-1,-1;IRI "IRI" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,IRI,-1,-1,hpms_2018_fsys456_2019_10_21,IRI,-1,-1;IRI_YEAR "IRI_YEAR" true true false 8 Date 0 0,First,#,hpms_2018_fsys123_2019_10_21,IRI_YEAR,-1,-1,hpms_2018_fsys456_2019_10_21,IRI_YEAR,-1,-1;NHS "NHS" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,NHS,-1,-1,hpms_2018_fsys456_2019_10_21,NHS,-1,-1;OWNERSHIP "OWNERSHIP" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,OWNERSHIP,-1,-1,hpms_2018_fsys456_2019_10_21,OWNERSHIP,-1,-1;PSR "PSR" true true false 8 Double 0 0,First,#,hpms_2018_fsys123_2019_10_21,PSR,-1,-1,hpms_2018_fsys456_2019_10_21,PSR,-1,-1;ROUTE_NUMBER "ROUTE_NUMBER" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,ROUTE_NUMBER,-1,-1,hpms_2018_fsys456_2019_10_21,ROUTE_NUMBER,-1,-1;ROUTE_NAME "ROUTE_NAME" true true false 100 Text 0 0,First,#,hpms_2018_fsys123_2019_10_21,ROUTE_NAME,0,100,hpms_2018_fsys456_2019_10_21,ROUTE_NAME,0,100;ROUTE_QUALIFIER "ROUTE_QUALIFIER" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,ROUTE_QUALIFIER,-1,-1,hpms_2018_fsys456_2019_10_21,ROUTE_QUALIFIER,-1,-1;ROUTE_SIGNING "ROUTE_SIGNING" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,ROUTE_SIGNING,-1,-1,hpms_2018_fsys456_2019_10_21,ROUTE_SIGNING,-1,-1;SPEED_LIMIT "SPEED_LIMIT" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,SPEED_LIMIT,-1,-1,hpms_2018_fsys456_2019_10_21,SPEED_LIMIT,-1,-1;STRAHNET_TYPE "STRAHNET_TYPE" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,STRAHNET_TYPE,-1,-1,hpms_2018_fsys456_2019_10_21,STRAHNET_TYPE,-1,-1;STRUCTURE_TYPE "STRUCTURE_TYPE" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,STRUCTURE_TYPE,-1,-1,hpms_2018_fsys456_2019_10_21,STRUCTURE_TYPE,-1,-1;SURFACE_TYPE "SURFACE_TYPE" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,SURFACE_TYPE,-1,-1,hpms_2018_fsys456_2019_10_21,SURFACE_TYPE,-1,-1;THROUGH_LANES "THROUGH_LANES" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,THROUGH_LANES,-1,-1,hpms_2018_fsys456_2019_10_21,THROUGH_LANES,-1,-1;TOLL_CHARGED "TOLL_CHARGED" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,TOLL_CHARGED,-1,-1,hpms_2018_fsys456_2019_10_21,TOLL_CHARGED,-1,-1;TOLL_TYPE "TOLL_TYPE" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,TOLL_TYPE,-1,-1,hpms_2018_fsys456_2019_10_21,TOLL_TYPE,-1,-1;TRUCK "TRUCK" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,TRUCK,-1,-1,hpms_2018_fsys456_2019_10_21,TRUCK,-1,-1;URBAN_CODE "URBAN_CODE" true true false 4 Long 0 0,First,#,hpms_2018_fsys123_2019_10_21,URBAN_CODE,-1,-1,hpms_2018_fsys456_2019_10_21,URBAN_CODE,-1,-1;SHAPE_Length "SHAPE_Length" false true true 8 Double 0 0,First,#,hpms_2018_fsys123_2019_10_21,SHAPE_Length,-1,-1,hpms_2018_fsys456_2019_10_21,SHAPE_Length,-1,-1'
        add_source = "NO_SOURCE_INFO"
        arcpy.management.Merge(inputs, output, field_mappings, add_source)
    
    def repair_hpms_geometry(self):
        '''
        Summary: Repair geometry of HPMS road network
        '''
        arcpy.env.workspace = self.hpms_gdb
        arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("USA Contiguous Albers Equal Area Conic USGS")

        print("Repairing geometry of HPMS road network...")
        in_features = self.hpms_fc_123456
        out_features = "HPMS_2018_repair_geo"
        self.hpms_repair_geo = out_features
        where_clause = ""
        use_field_alias_as_name = "NOT_USE_ALIAS"
        sort_field = None
        arcpy.conversion.ExportFeatures(in_features, out_features, where_clause, use_field_alias_as_name, sort_field)

        in_features = "HPMS_2018_repair_geo"
        delete_null = "DELETE_NULL"
        validation_method = "ESRI"
        arcpy.management.RepairGeometry(in_features, delete_null, validation_method)
    
    def subset_hpms_geometry(self):
        '''
        Summary: Subset geometry to 50 states and Washington DC
        '''
        arcpy.env.workspace = self.hpms_gdb
        arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("USA Contiguous Albers Equal Area Conic USGS")

        print("Subsetting HPMS road network to 50 states and Washington DC...")

        fc_name = self.hpms_repair_geo
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
    
    def intersect_hpms_county(self):
        '''
        Summary: Intersect HPMS road network with US county boundaries
        '''
        arcpy.env.workspace = self.hpms_gdb
        arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("USA Contiguous Albers Equal Area Conic USGS")

        print("Intersecting HPMS road network with US county boundaries...")

        in_features="HPMS_2018_state_sub_proj;US_census_county_2020"
        out_feature_class="HPMS_2018_county_intxn"
        join_attributes="ALL"
        cluster_tolerance=None
        output_type="INPUT"
        arcpy.analysis.PairwiseIntersect(in_features, out_feature_class, join_attributes, cluster_tolerance, output_type)
    
    def add_unique_id(self):
        '''
        Summary: Generate new field with unique ID for road links
        '''
        arcpy.env.workspace = self.hpms_gdb
        arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("USA Contiguous Albers Equal Area Conic USGS")

        print("Calculating new field for road link FID: [FID_Link_Cnty_Intxn]")

        inFeatures = "HPMS_2018_county_intxn"
        fieldName = "FID_Link_Cnty_Intxn"
        arcpy.management.AddField(inFeatures, fieldName, "LONG")
        expression = "!OBJECTID!"
        expression_type = "PYTHON3"
        arcpy.management.CalculateField(inFeatures, fieldName, expression, expression_type)
    
    def correct_urban_codes(self):
        '''
        Summary: Correct urban codes in HPMS data (including links with no urban code)
        '''
        arcpy.env.workspace = self.hpms_gdb
        arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("USA Contiguous Albers Equal Area Conic USGS")

        print("Correcting urban codes in HPMS data...")

        target_features = "HPMS_2018_county_intxn"
        join_features = "US_census_uac_2010"
        out_feature_class = "HPMS_2018_cnty_uac_join"
        join_operation = "JOIN_ONE_TO_ONE"
        join_type = "KEEP_ALL"
        field_mapping='FID_HPMS_2018_state_sub_proj "FID_HPMS_2018_state_sub_proj" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,FID_HPMS_2018_state_sub_proj,-1,-1;Year_Record "Year_Record" true true false 2 Short 0 0,First,#,HPMS_2018_county_intxn,Year_Record,-1,-1;State_Code "State_Code" true true false 2 Short 0 0,First,#,HPMS_2018_county_intxn,State_Code,-1,-1;Route_ID "Route_ID" true true false 2048 Text 0 0,First,#,HPMS_2018_county_intxn,Route_ID,0,2048;Begin_Point "Begin_Point" true true false 8 Double 0 0,First,#,HPMS_2018_county_intxn,Begin_Point,-1,-1;End_Point "End_Point" true true false 8 Double 0 0,First,#,HPMS_2018_county_intxn,End_Point,-1,-1;AADT "AADT" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,AADT,-1,-1;AADT_COMBINATION "AADT_COMBINATION" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,AADT_COMBINATION,-1,-1;AADT_SINGLE_UNIT "AADT_SINGLE_UNIT" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,AADT_SINGLE_UNIT,-1,-1;ACCESS_CONTROL_ "ACCESS_CONTROL_" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,ACCESS_CONTROL_,-1,-1;COUNTY_CODE "COUNTY_CODE" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,COUNTY_CODE,-1,-1;F_SYSTEM "F_SYSTEM" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,F_SYSTEM,-1,-1;FACILITY_TYPE "FACILITY_TYPE" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,FACILITY_TYPE,-1,-1;IRI "IRI" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,IRI,-1,-1;IRI_YEAR "IRI_YEAR" true true false 8 Date 0 0,First,#,HPMS_2018_county_intxn,IRI_YEAR,-1,-1;NHS "NHS" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,NHS,-1,-1;OWNERSHIP "OWNERSHIP" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,OWNERSHIP,-1,-1;PSR "PSR" true true false 8 Double 0 0,First,#,HPMS_2018_county_intxn,PSR,-1,-1;ROUTE_NUMBER "ROUTE_NUMBER" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,ROUTE_NUMBER,-1,-1;ROUTE_NAME "ROUTE_NAME" true true false 100 Text 0 0,First,#,HPMS_2018_county_intxn,ROUTE_NAME,0,100;ROUTE_QUALIFIER "ROUTE_QUALIFIER" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,ROUTE_QUALIFIER,-1,-1;ROUTE_SIGNING "ROUTE_SIGNING" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,ROUTE_SIGNING,-1,-1;SPEED_LIMIT "SPEED_LIMIT" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,SPEED_LIMIT,-1,-1;STRAHNET_TYPE "STRAHNET_TYPE" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,STRAHNET_TYPE,-1,-1;STRUCTURE_TYPE "STRUCTURE_TYPE" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,STRUCTURE_TYPE,-1,-1;SURFACE_TYPE "SURFACE_TYPE" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,SURFACE_TYPE,-1,-1;THROUGH_LANES "THROUGH_LANES" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,THROUGH_LANES,-1,-1;TOLL_CHARGED "TOLL_CHARGED" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,TOLL_CHARGED,-1,-1;TOLL_TYPE "TOLL_TYPE" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,TOLL_TYPE,-1,-1;TRUCK "TRUCK" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,TRUCK,-1,-1;URBAN_CODE "URBAN_CODE" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,URBAN_CODE,-1,-1;FID_US_census_county_2020 "FID_US_census_county_2020" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,FID_US_census_county_2020,-1,-1;STATEFP "STATEFP" true true false 2 Text 0 0,First,#,HPMS_2018_county_intxn,STATEFP,0,2;COUNTYFP "COUNTYFP" true true false 3 Text 0 0,First,#,HPMS_2018_county_intxn,COUNTYFP,0,3;COUNTYNS "COUNTYNS" true true false 8 Text 0 0,First,#,HPMS_2018_county_intxn,COUNTYNS,0,8;GEOID "GEOID" true true false 5 Text 0 0,First,#,HPMS_2018_county_intxn,GEOID,0,5;NAME "NAME" true true false 100 Text 0 0,First,#,HPMS_2018_county_intxn,NAME,0,100;NAMELSAD "NAMELSAD" true true false 100 Text 0 0,First,#,HPMS_2018_county_intxn,NAMELSAD,0,100;Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,HPMS_2018_county_intxn,Shape_Length,-1,-1;FID_Link_Cnty_Intxn "FID_Link_Cnty_Intxn" true true false 4 Long 0 0,First,#,HPMS_2018_county_intxn,FID_Link_Cnty_Intxn,-1,-1;UACE10 "UACE10" true true false 5 Text 0 0,First,#,US_census_uac_2010,UACE10,0,5;GEOID10 "GEOID10" true true false 5 Text 0 0,First,#,US_census_uac_2010,GEOID10,0,5;NAME10 "NAME10" true true false 100 Text 0 0,First,#,US_census_uac_2010,NAME10,0,100;NAMELSAD10 "NAMELSAD10" true true false 100 Text 0 0,First,#,US_census_uac_2010,NAMELSAD10,0,100;UATYP10 "UATYP10" true true false 1 Text 0 0,First,#,US_census_uac_2010,UATYP10,0,1;Shape_Length_1 "Shape_Length" false true true 8 Double 0 0,First,#,US_census_uac_2010,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0,First,#,US_census_uac_2010,Shape_Area,-1,-1'
        match_option="HAVE_THEIR_CENTER_IN"
        search_radius=None
        distance_field_name=""
        arcpy.analysis.SpatialJoin(target_features, join_features, out_feature_class, join_operation, join_type, field_mapping, match_option, search_radius, distance_field_name)


def main():
    STORAGE_DIR = Path("../data/processed_data")

    if ARCPY == True:
        DataPrep = ArcPyHPMSDataPreparation(STORAGE_DIR)
    else:
        DataPrep = HPMSDataPreparation(STORAGE_DIR)
    
    DataPrep.copy_raw_hpms(Path("../data/raw_data/HPMS/HPMS_2018.gdb"))
    DataPrep.copy_raw_census(Path("../data/raw_data/census/US_county_2020.shp"))
    DataPrep.copy_raw_census_urban(Path("../data/raw_data/census/US_uac_2010.shp"))
    DataPrep.copy_raw_census_blocks(Path("../data/raw_data/census/blocks"))

    DataPrep.merge_hpms_data()
    DataPrep.repair_hpms_geometry()
    DataPrep.subset_hpms_geometry()
    DataPrep.intersect_hpms_county()
    DataPrep.add_unique_id()
    DataPrep.correct_urban_codes()

if __name__ == '__main__':
    main()

