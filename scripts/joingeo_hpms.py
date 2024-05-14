"""
HPMS Data Paper
by Aviral Chawla, Meg Fay, and Britanny Antonczak

Summary: This script 
1) This script converts the HPMS road link AADT estimation results to spatial data,
2) Calculates the length of road segments in miles and kilometers, and 
3) Calculates the vehicle miles traveled (VMT) and vehicle kilometers traveled (VKT) for all vehicle classes.

<LICENSE>
"""

# TODO: Add suitable comments

import arcpy
import sys
import numpy as np
from pathlib import Path

arcpy.env.overwriteOutput = True
print('arcpy.env.overwriteOutput', arcpy.env.overwriteOutput,'\n')

arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("USA Contiguous Albers Equal Area Conic USGS")

def getFieldNames(in_table):
        field_names = [f.name for f in arcpy.ListFields(in_table)]
        return field_names

def import_to_gdb(in_table, tab_out_gdb, tab_out_name):
    '''
    Summary: This function imports the results table to the HPMS geodatabase.
    Inputs:
        - in_table: path to the input table
        - tab_out_gdb: path to the output geodatabase
        - tab_out_name: name of the output table
    '''
    print("Importing results table to the geodatabase...")

    try:
            if arcpy.Exists(tab_out_gdb + "\\" + tab_out_name):
                    arcpy.Delete_management(tab_out_gdb + "\\" + tab_out_name)
            arcpy.conversion.TableToTable(in_table, tab_out_gdb, tab_out_name)
            print('Imported results table to the following path:\n{}'.format(tab_out_gdb + "\\" + tab_out_name))

    except Exception as e:
            print(arcpy.GetMessages())
            print("ERROR: ")
            print(e)
            sys.exit('Exiting script.')

def create_geometry(in_feature, keep_fields, geo_out_gdb, geo_out_name):
    '''
    Summary: This function creates a new geometry feature class to store the HPMS road link AADT estimation results.
    Inputs:
        - in_feature: path to the input feature class
        - keep_fields: list of fields to keep
        - geo_out_gdb: path to the output geodatabase
        - geo_out_name: name of the output feature class
    '''
    print("Creating new geometry feature class...")
    try:
            field_mappings = arcpy.FieldMappings()
            for field in keep_fields:
                    fmap = arcpy.FieldMap()
                    fmap.addInputField(in_feature, field) 
                    fmap.mergeRule = "First"
                    field_mappings.addFieldMap(fmap)
            
            arcpy.FeatureClassToFeatureClass_conversion(in_feature, geo_out_gdb, geo_out_name, '', field_mapping = field_mappings)
            print('Generated new geometry feature class:\n{}'.format(geo_out_gdb + "\\" + geo_out_name))

    except Exception as e:
            print(arcpy.GetMessages())
            print("ERROR: ")
            print(e)
            sys.exit('Exiting script.')

def join_results(in_feature, join_table, in_field, join_field, fields, field_remove):
        '''
        Summary: This function joins the HPMS road link AADT estimation results to the new geometry feature class.
        Inputs:
            - in_feature: path to the input feature class
            - join_table: path to the table to join
            - in_field: field in the input feature class
            - join_field: field in the join table
            - fields: list of fields to join
        '''

        print("Joining results to the geometry feature class...")
        
        for field in field_remove:
                if field in fields:
                        fields.remove(field)
        
        try:
                arcpy.management.JoinField(in_feature, in_field, join_table, join_field, fields)
                print('Joined the following results fields to the geometry feature class:\n{}'.format(fields))
            
        except Exception as e:
                print(arcpy.GetMessages())
                print("ERROR: ")
                print(e)
                sys.exit('Exiting script.')

def calculate_geometry_length(in_table, field_name, field_type, length_unit):
    '''
    Summary: This function calculates the length of each road link in meters.
    Inputs:
        - in_table: path to the input table
        - field_name: name of the new field
        - field_type: type of the new field
    '''
    
    print("Calculating geometry length...")
    try:
        arcpy.AddField_management(in_table, field_name, field_type)
    except Exception as e:
        arcpy.GetMessages()
        print("ERROR: ")
        print(e)
        sys.exit('Exiting script.')

    in_feature = in_table
    geometry_property = [[field_name, "LENGTH"]]
    area_unit = ''
    try:
        arcpy.management.CalculateGeometryAttributes(in_feature, geometry_property, length_unit, area_unit)
        print('Calculated new field for intersection area: {}'.format(field_name))
    except Exception as e:
        print(arcpy.GetMessages())
        print("ERROR: ")
        print(e)
        sys.exit('Exiting script.')

def calculate_vmt_vkt(in_table, field_names):
        '''
        Summary: This function calculates the vehicle miles traveled (VMT) and vehicle kilometers traveled (VKT) for all vehicle classes.
        Inputs:
                - in_table: path to the input table
                - field_names: list of field names
        '''
        
        print("Calculating VMT and VKT...")
        field_type = "DOUBLE"
        for field_name in field_names:
                try:
                        arcpy.AddField_management(in_table, field_name, field_type)
                except Exception as e:
                        arcpy.GetMessages()
                        print("ERROR: ")
                        print(e)
                        sys.exit('Exiting script.')
        
        arcpy.CalculateField_management(in_table, 'VMT_MDV', '!AADT_MDV! * (!Shape_Length_New! / 1609.34)', "PYTHON3")
        arcpy.CalculateField_management(in_table, 'VKT_MDV', '!AADT_MDV! * (!Shape_Length_New! / 1000)', "PYTHON3")
        
        arcpy.CalculateField_management(in_table, 'VMT_HDV', '!AADT_HDV! * (!Shape_Length_New! / 1609.34)', "PYTHON3")
        arcpy.CalculateField_management(in_table, 'VKT_HDV', '!AADT_HDV! * (!Shape_Length! / 1000)', "PYTHON3")
        
        arcpy.CalculateField_management(in_table, 'VMT_TOTAL', '!AADT! * (!Shape_Length_New! / 1609.34)', "PYTHON3")
        arcpy.CalculateField_management(in_table, 'VKT_TOTAL', '!AADT! * (!Shape_Length_New! / 1000)', "PYTHON3")


def main():
    HPMS_DIR = Path('../data/processed_data/HPMS/HPMS.gdb')
    GEO_IN_PATH = HPMS_DIR / 'HPMS_2018_county_intxn'
    TAB_IN_PATH = HPMS_DIR / '..' / 'hpms_aadt_imputed.csv'
    
    GEO_JOIN_FIELD = 'FID_Link_Cnty_Intxn'
    TAB_JOIN_FIELD = 'FID_Link_Cnty_Intxn'

    OUT_NAME = 'hpms_aadt_imputation'
    TAB_OUT_NAME = OUT_NAME + '_table'

    import_to_gdb(in_table = str(TAB_IN_PATH.absolute()), 
                  tab_out_gdb = str(HPMS_DIR.absolute()), 
                  tab_out_name = TAB_OUT_NAME)
    create_geometry(in_feature = str(GEO_IN_PATH.absolute()),
                    keep_fields = [GEO_JOIN_FIELD, 'Shape_Length'], 
                    geo_out_gdb = str(HPMS_DIR.absolute()), 
                    geo_out_name = OUT_NAME)
    join_results(in_feature = str((HPMS_DIR / OUT_NAME).absolute()),
                 join_table = str((HPMS_DIR / TAB_OUT_NAME).absolute()),
                 in_field = GEO_JOIN_FIELD, 
                 join_field = TAB_JOIN_FIELD,
                 fields = getFieldNames(str((HPMS_DIR / TAB_OUT_NAME).absolute())),
                 field_remove = ['OBJECTID', 'Shape_Length', 'Shape_Area', TAB_JOIN_FIELD, 'Shape_Length_'])
    calculate_geometry_length(in_table = str((HPMS_DIR / OUT_NAME).absolute()), 
                              field_name = 'Shape_Length_New', 
                              field_type = 'DOUBLE',
                              length_unit = 'METERS')
    calculate_vmt_vkt(in_table = str((HPMS_DIR / OUT_NAME).absolute()), 
                      field_names = ['VMT_MDV', 'VKT_MDV', 'VMT_HDV', 'VKT_HDV', 'VMT_TOTAL', 'VKT_TOTAL'])


if __name__ == '__main__':
        main()