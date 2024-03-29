import pandas as pd
import geopandas as gpd
import numpy as np
import os
import time
import datetime
import sys
import us
from osgeo import ogr
import pyogrio
import pyarrow
import sys

# load data
hpms_gdb = "Z:\\ROAD_AQ\\HPMS Traffic Data\\HPMS\\HPMS_test.gdb"
data_hpms = gpd.read_file(hpms_gdb, layer='HPMS_aadt_imputation', engine="pyogrio", use_arrow=True)

# get geometry length
data_hpms['geom_length_km'] = data_hpms['geometry'].length / 1000
data_hpms['geom_length_miles'] = data_hpms['geometry'].length / 1609.34

# calculate vmt and vkt using aadt
data_hpms['vmt_mdv_calc'] = data_hpms['AADT_MDV'] * data_hpms['geom_length_miles']
data_hpms['vkt_mdv_calc'] = data_hpms['AADT_MDV'] * data_hpms['geom_length_km']

data_hpms['vmt_hdv_calc'] = data_hpms['AADT_HDV'] * data_hpms['geom_length_miles']
data_hpms['vkt_hdv_calc'] = data_hpms['AADT_HDV'] * data_hpms['geom_length_km']

data_hpms['vmt_total_calc'] = data_hpms['AADT'] * data_hpms['geom_length_miles']
data_hpms['vkt_total_calc'] = data_hpms['AADT'] * data_hpms['geom_length_km']

# save
data_hpms.to_file("Z:\\ROAD_AQ\\HPMS Traffic Data\\HPMS\\HPMS_test.gdb", layer='HPMS_vmt', driver="OpenFileGDB")