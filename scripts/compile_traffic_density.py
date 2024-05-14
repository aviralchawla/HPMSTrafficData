import arcpy
import pandas as pd
from pathlib import Path

arcpy.env.overwriteOutput = True
print('arcpy.env.overwriteOutput', arcpy.env.overwriteOutput,'\n')

arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("USA Contiguous Albers Equal Area Conic USGS")
pd.set_option('display.float_format', '{:.4f}'.format)

def merge_state_fcs(TD_GDB):
    
    print("Merging state census block feature classes...")
    
    state_fcs = arcpy.ListFeatureClasses()
    inputs = state_fcs
    output = f"{TD_GDB}\\US_census_block_2020"
    arcpy.Merge_management(inputs, output)


def calculate_census_block_area(TD_GDB):

    print('Calculating census block area...')

    in_table = f"{TD_GDB}\\US_census_block_2020"
    field_name = "Area_Orig"
    field_type = "DOUBLE"
    arcpy.AddField_management(in_table, field_name, field_type)

    geometry_property = [[field_name, "AREA"]]
    length_unit = ''
    area_unit = 'SQUARE_MILES_US'
    arcpy.CalculateGeometryAttributes_management(in_table, geometry_property, length_unit, area_unit)

def copy_hpms_data(TD_GDB, HPMS_GDB, fc):

    print('Copying HPMS data...')

    in_data = f"{HPMS_GDB}\\{fc}"
    out_data = f"{TD_GDB}\\{fc}"

    arcpy.Copy_management(in_data, out_data)

def buffer_census_blocks(TD_GDB, distance):

    print('Buffering census blocks...')

    in_feature = f"{TD_GDB}\\US_census_block_2020"
    out_feature = f"{TD_GDB}\\US_census_block_buffers"
    buffer_distance = f'{distance} Meters'
    dissolve_option = 'NONE'
    dissolve_field = None
    method = 'PLANAR'
    max_deviation = '0 Meters'

    arcpy.analysis.PairwiseBuffer(in_feature, out_feature, buffer_distance, dissolve_option, dissolve_field, method, max_deviation)

def buffer_area_addfield(TD_GDB):
    
    print('Creating Buffer Area Field...')

    in_feature = f"{TD_GDB}\\US_census_block_buffers"
    field_name = "Area_Buffer"
    field_type = "DOUBLE"

    arcpy.management.AddField(in_feature, field_name, field_type)

def buffer_area_calculate(TD_GDB):

    print('Calculating buffer area...')

    in_feature = f"{TD_GDB}\\US_census_block_buffers"
    field_name = "Area_Buffer"
    geometry_property = [[field_name, "AREA"]]
    length_unit = ''
    area_unit = 'SQUARE_METERS'

    arcpy.management.CalculateGeometryAttributes(in_feature, geometry_property, length_unit, area_unit)

def intersect_buffer_roads(TD_GDB):

    print('Intersecting buffer and roads...')

    buffs_fc = f"{TD_GDB}\\US_census_block_buffers"
    roads_fc = f"{TD_GDB}\\HPMS_2018_vmt"

    in_fcs = [buffs_fc, roads_fc]
    out_fc = f"{TD_GDB}\\density_intxn"

    arcpy.analysis.PairwiseIntersect(in_fcs, out_fc)


def main():
    TD_GDB = Path('../data/processed_data/Traffic_Density/Traffic_Density.gdb')
    HPMS_GDB = Path('../data/processed_data/HPMS/HPMS.gdb')

    arcpy.env.workspace = str(TD_GDB.absolute())

    merge_state_fcs(TD_GDB)
    calculate_census_block_area(TD_GDB)
    copy_hpms_data(TD_GDB, HPMS_GDB, 'hpms_aadt_imputation')

    buffer_census_blocks(TD_GDB, distance = 250)
    buffer_area_addfield(TD_GDB)
    buffer_area_calculate(TD_GDB)

    intersect_buffer_roads(TD_GDB)

if __name__ == '__main__':
    main()



