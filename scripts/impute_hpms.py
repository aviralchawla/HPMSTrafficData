"""
HPMS Data Paper
by Aviral Chawla, Meg Fay, and Britanny Antonczak

Summary: This script 
1) Creates two file geodatabases for storing processed data,
2) Compiles the raw data into two file geodatabases for analysis, 
3) Cleans and merges the HPMS network, intersects HPMS links with US county census boundaries, and adds rural-urban codes to road links in the network.

<LICENSE>
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import os
import sys
import us
from osgeo import ogr
import fiona
from pathlib import Path

def load_data(gdb, layer):
  return gpd.read_file(gdb, layer=layer, engine='pyogrio', use_arrow=True)

def correct_hpms_columns(hpms):
  '''
  Summary: This function corrects the columns in the HPMS dataset to ensure that the data is in the correct format for analysis.
  Inputs: 
    -hpms (DataFrame) - The HPMS dataset
  Outputs:
    -hpms (DataFrame) - The corrected HPMS dataset
  '''

  # Setting correct format since the data is not preserved in the geodatabase
  hpms['GEOID'] = hpms['GEOID'].str.zfill(5)
  hpms['STATEFP'] = hpms['STATEFP'].str.zfill(2)
  hpms['COUNTYFP'] = hpms['COUNTYFP'].str.zfill(3)
  hpms['F_SYSTEM'] = hpms['F_SYSTEM'].astype('category')

  hpms.rename(columns={'AADT_COMBINATION': 'AADT_HDV', 'AADT_SINGLE_UNIT': 'AADT_MDV'}, inplace=True)

  # Estimate the number of through lanes for road segments with no data. Set value to '2' if no data (See Note)
  hpms['THROUGH_LANES'] = hpms['THROUGH_LANES'].fillna(0).replace(0, 2)

  hpms.sort_values(['STATEFP', 'COUNTYFP', 'F_SYSTEM'], inplace=True)

  hpms.rename(columns={'URBAN_CODE': 'ORIG_URBAN_CODE'}, inplace=True)

  # Join additional state information from us package
  states_info = pd.DataFrame([(state.fips, state.name) for state in us.states.STATES], columns=['STATEFP', 'STATENAME'])
  hpms = hpms.merge(states_info, on='STATEFP', how='left')

  # clean the final output
  hpms = hpms.apply(lambda x: x.replace([np.inf, -np.inf], np.nan))

  return hpms

def merge_uac_data(hpms, hpms_uac):

  hpms_uac = hpms_uac[['FID_Link_Cnty_Intxn', 'UACE10', 'UATYP10']]
  hpms = hpms.merge(hpms_uac, on='FID_Link_Cnty_Intxn', how='left')
  hpms['NEW_URBAN_CODE'] = hpms['UATYP10'].map({'U': hpms['UACE10'], 'C': '99998'}).fillna('99999')
  hpms.drop(['UATYP10', 'UACE10'], axis=1, inplace=True)
  hpms['NEW_URBAN_CODE'] = hpms['NEW_URBAN_CODE'].astype(str)
  hpms['URBAN'] = hpms['NEW_URBAN_CODE'].map({'99999': 0, '99998': 2}).fillna(1)
  hpms['URBAN'] = hpms['URBAN'].astype('category')

  return hpms

def calculate_vkt_vmt(hpms):
  
  hpms['VKT'] = hpms['AADT'] * hpms['Shape_Length'] / 1000
  hpms['VMT'] = hpms['AADT'] * hpms['Shape_Length'] / 1609.344
  hpms['VKT_MDV'] = hpms['AADT_MDV'] * hpms['Shape_Length'] / 1000
  hpms['VMT_MDV'] = hpms['AADT_MDV'] * hpms['Shape_Length'] / 1609.344
  hpms['VKT_HDV'] = hpms['AADT_HDV'] * hpms['Shape_Length'] / 1000
  hpms['VMT_HDV'] = hpms['AADT_HDV'] * hpms['Shape_Length'] / 1609.344
  hpms['VKT_LDV'] = hpms['VKT'] - hpms['VKT_MDV'] - hpms['VKT_HDV']
  hpms['VMT_LDV'] = hpms['VMT'] - hpms['VMT_MDV'] - hpms['VMT_HDV']
  
  return hpms

def subset_hpms(hpms):

  sub_aadt_nazero = hpms[(hpms['AADT'] == 0) | (hpms['AADT'].isna())]

  AADT_HDV_temp = hpms['AADT_HDV'].fillna(0)
  AADT_MDV_temp = hpms['AADT_MDV'].fillna(0)

  sub_aadt_neg = hpms[(hpms['AADT'] > 0) & (hpms['AADT'] < (AADT_HDV_temp + AADT_MDV_temp))]
  sub_aadt_errors = hpms[hpms['FID_Link_Cnty_Intxn'].isin(sub_aadt_nazero['FID_Link_Cnty_Intxn'].tolist() + sub_aadt_neg['FID_Link_Cnty_Intxn'].tolist())]
  hpms_sub = hpms[~hpms['FID_Link_Cnty_Intxn'].isin(sub_aadt_errors['FID_Link_Cnty_Intxn'])]
  
  target_columns = ['FID_Link_Cnty_Intxn', 'STATEFP', 'STATENAME', 'COUNTYFP', 'GEOID', 'F_SYSTEM',
           'NEW_URBAN_CODE', 'URBAN', 'THROUGH_LANES', 'LANE_KMS', 'LANE_MILES', 'VKT', 'VMT',
           'AADT', 'AADT_MDV', 'AADT_HDV', 'Shape_Length']
  
  hpms_sub = hpms_sub[target_columns]
  hpms_sub = hpms_sub.rename(columns={'NEW_URBAN_CODE': 'URBAN_CODE'})
  hpms_sub = hpms_sub.apply(lambda col: col.replace([np.nan, np.inf, -np.inf], np.nan) if col.dtype.kind in 'fi' else col)

  return hpms_sub


def main():
  HPMS_GDB = Path('../data/processed_data/HPMS/HPMS.gdb')

  hpms_intx = load_data(HPMS_GDB, layer='HPMS_2018_county_intxn')
  hpms_uac = load_data(HPMS_GDB, layer='HPMS_2018_cnty_uac_join')

  target_fields = ['FID_Link_Cnty_Intxn', 'STATEFP', 'COUNTYFP', 'GEOID', 'F_SYSTEM', 
             'THROUGH_LANES', 'URBAN_CODE'] + [col for col in hpms_intx.columns if 'AADT' in col] + ['Shape_Length']

  hpms_intx = hpms_intx[target_fields]
  hpms_intx = correct_hpms_columns(hpms_intx)
  

  # calculate VKT, VMT, lane kms, and lane miles for analysis
  hpms_intx = calculate_vkt_vmt(hpms_intx)
  hpms_intx['LANE_KMS'] = hpms_intx['THROUGH_LANES'] * (hpms_intx['Shape_Length'] / 1000)
  hpms_intx['LANE_MILES'] = hpms_intx['THROUGH_LANES'] * (hpms_intx['Shape_Length'] / 1609.344)

  # helps us find links located in urban area codes
  hpms_intx = merge_uac_data(hpms_intx, hpms_uac)
  hpms_intx['ORIG_URBAN_CODE'] = [_.split('.')[0] for _ in hpms_intx['ORIG_URBAN_CODE'].astype(str)] # remove decimal points
  hpms_intx['NEW_URBAN_CODE'] = hpms_intx['NEW_URBAN_CODE'].astype(str)
  hpms_intx['UAC_IS_SAME'] = (hpms_intx['ORIG_URBAN_CODE'] == hpms_intx['NEW_URBAN_CODE']).astype(int)

  hpms_sub = subset_hpms(hpms_intx)

  hpms_sub.to_csv(HPMS_GDB / '..' / 'hpms_aadt_subset.csv', index=False)