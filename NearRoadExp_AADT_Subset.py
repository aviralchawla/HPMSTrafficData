"""

HPMS Data Project - Near-Road Exposure

Last Updated: 02/21/2024
Created by Brittany Antonczak and Meg Fay
University of Vermont, Burlington, VT

"""

############################## ABOUT THIS SCRIPT ##############################
#                                                                             #
# This script inspects and prepares the HPMS dataset for estimation           #
# and analysis. Data subsetting includes: removing road links with no         #
# estimate of total AADT, estimates the the number of through lanes for road  #
# links with no available estimate, corrects road link census urban area      #
# codes, and rearranges and renames fields.                                   #
#                                                                             #
############################## ABOUT THIS SCRIPT ##############################

# ----- DETAILS ON DATA ----- 

# Data: FHWA 2018 highway performance monitoring system (HPMS) traffic data

# >>>> Important Fields: <<<<

# STATE_CODE - State FIPS Code

# F_SYSTEM - FHWA Functional Classifications
#       HPMS-defined Federal-Aid System Code & Description:
#       1	- Interstate
#       2	- Principal Arterial - Other Freeways and Expressways
#       3	- Principal Arterial - Other
#       4	- Minor Arterial
#       5	- Major Collector
#       6	- Urban Minor Collector
#       7 - Local 
#       Interstate is a Designation. The other functional Classifications 
#       are more subjective, although, they have division approval. 
#       (Roff, Thomas FHWA)

# AADT - Average Annual Daily Traffic
#       Annual Average Daily Traffic and represents all days of the  
#       reporting year for traffic on a section of road and is required 
#       for all Federal-aid highways and grade-separated interchange ramps.

# AADT_COMBINATION - Average Annual Daily Combination Truck Traffic
#       AADT for Combination Trucks and must be reported for the entire 
#       NHS and all Sample Panel sections. This item requires detailed
#       vehicle classification data and includes FHWA vehicle classes 8-13 
#       (four-or-less axle, single-trailer trucks through seven-or-more axle, 
#       multitrailer trucks). 

# AADT_SINGLE_UNIT - Average Annual Daily Single Unit Truck Traffic
#       AADT for single-unit trucks and buses and is required for all
#       National Highway System (NHS) and Sample Panel sections. Requires
#       detailed vehicle classification data and includes FHWA vehicle 
#       classes 4-7 (buses through four-or-more axle, single-unit trucks).

# THROUGH_LANES - The number of lanes designated for through-traffic.
#       The number of through lanes in both directions carrying through traffic 
#       in the off-peak period. Data may be reported independently for both 
#       directions of travel associated with divided highway sections, for 
#       which dual carriageway GIS network representation is required.

# URBAN_CODE - UACE (Urban Area Census Code)
#       Census urban code is up to five digits. Code 99999 for rural sections 
#       and 99998 for small urban sections (not within the adjusted urbanized 
#       area and with an urban population of at least 5,000). 
#         99999 = < 5,000*, 99998 = 5,000 - 49,000*
#         * Population is based on the 2010 Decennial Census.
#      	Areas with population less than 5000 are considered Rural and have a 
#       Urban Code of 99999. Census has Boundaries for populations greater than 
#       2500 where FHWA is Greater than 5000. Areas with Populations between 
#       5000 and 50000 are grouped together as Small Urban and use the 
#       Urban_Code = 99998. 

# ------------------------------------------------------------------------- #

# script title
print('''--- Near-Road Exposure: HPMS Data Subset ---''','\n')

# import packages

import pandas as pd
import geopandas as gpd
import numpy as np
import os
import time
import datetime
import sys
import tigris
from osgeo import ogr

# print current date and time
dt = datetime.datetime.now()
print ("Current date and time:",dt.strftime("%Y-%m-%d %H:%M:%S"),'\n\n')

# set start time for total execution time calculation
start_time_total = time.time()

# ----- SET LOCAL VARIABLES ---------------------------------------------------
print("Setting local variables...")

# set path of file geodatabase containing input HPMS data:
hpms_gdb = "//netfiles02.uvm.edu/trc_projects/ROAD_AQ/HPMS Traffic Data/HPMS/HPMS_test.gdb"

# inspect data in input file geodatabase(s)
# list all feature classes in file geodatabase(s)
driver = ogr.GetDriverByName('OpenFileGDB')
dataSource = driver.Open(hpms_gdb, 0)
fc_list = [dataSource.GetLayerByIndex(i).GetName() for i in range(dataSource.GetLayerCount())]
print(fc_list)

# set feature class name of input HPMS data:
hpms_fc = "HPMS_2018_county_intxn"

# set path of file geodatabase containing input HPMS census urban area code data:
# * this data is required to correct urban area codes in the HPMS data *
hpms_uac_gdb = "//netfiles02.uvm.edu/trc_projects/ROAD_AQ/HPMS Traffic Data/HPMS/HPMS_test.gdb"

# set feature class name of input HPMS:
# * data should contain road link ID and census urban area code *
hpms_uac_fc = "HPMS_2018_cnty_uac_join"

# set main output directory:
main_out_dir = "//netfiles02.uvm.edu/trc_projects/ROAD_AQ/HPMS Traffic Data/HPMS/AADT Subset"

# set additional output directories:
# * the following folders will be created if they do not already exist *
out_dir = os.path.join(main_out_dir, "HPMS Dataset")
os.makedirs(out_dir, exist_ok=True)

print("Local variables set.")

# ----- DEFINE FUNCTIONS ------------------------------------------------------- 
print("Defining functions...")

# FUNCTION: export table to CSV in directory
def my_table_export(df, file_name, out_dir):
    # set file path for table export
    file_path = os.path.join(out_dir, f"{file_name.rstrip('.csv')}.csv")
    
    # write csv
    df.to_csv(file_path, index=False)
    
    # print new export message 
    print("* Exported table to the following path:")
    print(file_path)

print("Functions defined.")

# ----- LOAD DATA --------------------------------------------------------------
print("Loading data...")

# remove scientific notation 
pd.set_option('display.float_format', '{:.4f}'.format)

# check that all file paths exist
file_paths = [hpms_gdb, hpms_uac_gdb, main_out_dir]

for file_path in file_paths:
    if not os.path.exists(file_path):
        print(f"ERROR: The file or directory does not exist: {file_path}")
        sys.exit()
    else: 
        print(f"File or directory exists: {file_path}")

try: 
    # load input HPMS data
    data_hpms = gpd.read_file(hpms_gdb, layer=hpms_fc)

    # load input HPMS data census urban area codes data
    data_hpms_uac = gpd.read_file(hpms_uac_gdb, layer=hpms_uac_fc).drop(columns='geometry')
except Exception as e:
    print(f"ERROR: An error occurred while loading the data: {e}")
    print(f"ERROR: The script will terminate.")
    sys.exit()  

print("Data loaded.")

# ----- PREP DATA --------------------------------------------------------------
print("Preparing data...")

hpms = data_hpms.copy()

# Select fields
hpms = hpms[['FID_Link_Cnty_Intxn', 'STATEFP', 'COUNTYFP', 'GEOID', 'F_SYSTEM', 
             'THROUGH_LANES', 'URBAN_CODE'] + [col for col in hpms.columns if 'AADT' in col] + ['Shape_Length']]

# Convert spatial data to non-spatial data
hpms = hpms.drop(columns='geometry')

# Remove road segments with zero shape length
hpms = hpms[hpms['Shape_Length'] > 0]

# Correct state and county FIPS codes and set functional classification field as factor
hpms['GEOID'] = hpms['GEOID'].str.zfill(5)
hpms['STATEFP'] = hpms['STATEFP'].str.zfill(2)
hpms['COUNTYFP'] = hpms['COUNTYFP'].str.zfill(3)
hpms['F_SYSTEM'] = hpms['F_SYSTEM'].astype('category')

# Rename truck AADT fields
hpms.rename(columns={'AADT_COMBINATION': 'AADT_HDV', 'AADT_SINGLE_UNIT': 'AADT_MDV'}, inplace=True)

# Calculate total vehicle kilometers traveled (VKT) and vehicle miles traveled (VMT) for each road segment
hpms['VKT'] = hpms['AADT'] * (hpms['Shape_Length'] / 1000)  # meter to kilometer
hpms['VMT'] = hpms['AADT'] * (hpms['Shape_Length'] * (1 / 1609.344))  # meter to miles

# Estimate the number of through lanes for road segments with no data. Set value to '2' if no data (See Note)
hpms['THROUGH_LANES'] = hpms['THROUGH_LANES'].fillna(0).replace(0, 2)

# Estimate lane-miles for each road segment based on road segment length and number of lanes
hpms['LANE_KMS'] = hpms['THROUGH_LANES'] * (hpms['Shape_Length'] / 1000)
hpms['LANE_MILES'] = hpms['THROUGH_LANES'] * (hpms['Shape_Length'] / 1609.344)

# Replace all 'NaN' exposure values with 'NA'
hpms = hpms.apply(lambda x: x.replace([pd.np.inf, -pd.np.inf], pd.NA))

# Arrange data
hpms.sort_values(['STATEFP', 'COUNTYFP', 'F_SYSTEM'], inplace=True)

# Rename fields
hpms.rename(columns={'URBAN_CODE': 'ORIG_URBAN_CODE'}, inplace=True)

# Join additional state information from tigris package
states_info = states(cb=True, year=2020)
states_info = states_info[['STATEFP', 'NAME']].rename(columns={'NAME': 'STATENAME'})
hpms = hpms.merge(states_info, on='STATEFP', how='left')

# Join HPMS census urban area codes
data_hpms_uac = data_hpms_uac[['FID_Link_Cnty_Intxn', 'UACE10', 'UATYP10']]
hpms = hpms.merge(data_hpms_uac, on='FID_Link_Cnty_Intxn', how='left')

# Set new field for new urban code
hpms['NEW_URBAN_CODE'] = hpms['UATYP10'].map({'U': hpms['UACE10'], 'C': '99998'}).fillna('99999')

# Remove fields
hpms.drop(['UATYP10', 'UACE10'], axis=1, inplace=True)

# Set new field URBAN for urban and rural classification based on URBAN_CODE
  # Coding: 
  #   0 for rural area: URBAN_CODE of 99999 (99999 = < 5,000*)
  #   1 for urban area: URBAN_CODE not 99999 or 99998
  #   2 for small urban area: URBAN_CODE of 99998 (99998 = 5,000 - 49,000*)
  #   * Population is based on the 2010 Decennial Census.
hpms['URBAN'] = hpms['NEW_URBAN_CODE'].map({'99999': 0, '99998': 2}).fillna(1)

# Set URBAN field as factor
hpms['URBAN'] = hpms['URBAN'].astype('category')

# Note. Estimating the number of lane miles for road segments with no data
# was based on the following assumption, although rural minor collector and 
# urban/rural local roads are not included in this data set:
#  "When estimating rural and urban lane mileage, the U.S. Department of 
#   Transportation, Federal Highway Administration assumes that rural minor 
#   collector and urban/rural local roads are two lanes wide."
# https://www.bts.gov/content/estimated-us-roadway-lane-miles-functional-system


# Calculate the percentage of road links that maintained the same urban area  
# code and were assigned a different urban area code after the above correction  
# was performed.

hpms['UAC_IS_SAME'] = (hpms['ORIG_URBAN_CODE'] == hpms['NEW_URBAN_CODE']).astype(int)

pcnt_uac_same = len(hpms[hpms['UAC_IS_SAME'] == 1]) / len(hpms) * 100
pcnt_uac_diff = 100 - pcnt_uac_same

summary = pd.DataFrame({
    'pcnt_uac_same': [pcnt_uac_same],
    'pcnt_uac_diff': [pcnt_uac_diff]
})

print(summary)

print("Data prepared.")

# ----- INSPECT DATA -----------------------------------------------------------
print("Inspecting data...")

# >>> Create subsets of the data to characterize errors and missing data <<<

# create subset of data with missing AADT values
# AADT == 0 OR AADT == NA
sub_aadt_nazero = hpms[(hpms['AADT'] == 0) | (hpms['AADT'].isna())]
print(f"Number of observations with missing AADT values: {len(sub_aadt_nazero)}")

# create subset of data where total AADT values are less than the sum of AADT from medium and heavy duty vehicles 
# AADT > 0 AND AADT < AADT_HDV + AADT_MDV
AADT_HDV_temp = hpms['AADT_HDV'].fillna(0)
AADT_MDV_temp = hpms['AADT_MDV'].fillna(0)

sub_aadt_neg = hpms[(hpms['AADT'] > 0) & (hpms['AADT'] < (AADT_HDV_temp + AADT_MDV_temp))]
print(f"Number of observations with AADT < AADT_HDV + AADT_MDV where AADT > 0 : {len(sub_aadt_neg)}")

# create subset where (AADT == 0 OR AADT == NA) OR (AADT > 0 AND AADT < AADT_HDV + AADT_MDV))
# this represents the total number of observations with AADT errors
sub_aadt_errors = hpms[hpms['FID_Link_Cnty_Intxn'].isin(sub_aadt_nazero['FID_Link_Cnty_Intxn'].tolist() + sub_aadt_neg['FID_Link_Cnty_Intxn'].tolist())]
print(f"Number of observations with AADT errors: {len(sub_aadt_errors)}")

# create subset where there is medium duty AADT but no heavy duty AADT
# or there is heavy duty AADT but no medium duty AADT
# (AADT_HDV > 0 AND AADT_MDV == 0) OR (AADT_MDV > 0 AND AADT_HDV == 0)
sub_aadt_1type = hpms[~hpms['FID_Link_Cnty_Intxn'].isin(sub_aadt_errors['FID_Link_Cnty_Intxn']) &
                      (((hpms['AADT_HDV'] > 0) & (hpms['AADT_MDV'].isna() | (hpms['AADT_MDV'] == 0))) |
                       ((hpms['AADT_MDV'] > 0) & (hpms['AADT_HDV'].isna() | (hpms['AADT_HDV'] == 0))))]
print(f"Number of observations with only one type of truck AADT: {len(sub_aadt_1type)}")

# create a subset with missing through lane data, but no AADT errors
sub_aadt_lnnazeroerrorsrm = hpms[~hpms['FID_Link_Cnty_Intxn'].isin(sub_aadt_errors['FID_Link_Cnty_Intxn']) &
                                 ((hpms['THROUGH_LANES'].isna()) | 
                                  (hpms['THROUGH_LANES'] == "") |
                                  (hpms['THROUGH_LANES'] == " ") |
                                  (hpms['THROUGH_LANES'] == 0))]
print(f"Number of observations with missing through lane data: {len(sub_aadt_lnnazeroerrorsrm)}")

# >>> Calculate descriptive statistics of subsets <<<

summary_sub = pd.DataFrame({
    'pcnt_errors': [len(sub_aadt_errors) / len(hpms) * 100],
    'pcnt_1vehclassobsv': [len(sub_aadt_1type) / len(hpms) * 100],
    'pcnt_nolnmi': [len(sub_aadt_lnnazeroerrorsrm) / len(hpms) * 100]
})

print(summary_sub)

print("Data inspected.")

# ----- REMOVE ERRORS AND SUBSET VARIABLES --------------------------------------
print("Removing errors and subsetting variables...")

# Filter out the rows with FID_Link_Cnty_Intxn in sub_aadt_errors
hpms_sub = hpms[~hpms['FID_Link_Cnty_Intxn'].isin(sub_aadt_errors['FID_Link_Cnty_Intxn'])]

# Select the variables to keep
columns = ['FID_Link_Cnty_Intxn', 'STATEFP', 'STATENAME', 'COUNTYFP', 'GEOID', 'F_SYSTEM',
           'NEW_URBAN_CODE', 'URBAN', 'THROUGH_LANES', 'LANE_KMS', 'LANE_MILES', 'VKT', 'VMT',
           'AADT', 'AADT_MDV', 'AADT_HDV', 'Shape_Length']

# Subset the data with the selected columns
hpms_sub = hpms_sub[columns]

# Rename the 'NEW_URBAN_CODE' column to 'URBAN_CODE'
hpms_sub = hpms_sub.rename(columns={'NEW_URBAN_CODE': 'URBAN_CODE'})

# Replace all 'NaN' and infinite values with 'NA' in numeric columns
hpms_sub = hpms_sub.apply(lambda col: col.replace([np.nan, np.inf, -np.inf], np.nan) if col.dtype.kind in 'fi' else col)

# Print the number of rows in the DataFrame
num_rows = len(hpms_sub)
print(f"Number of rows in the HPMS subset data: {num_rows}")

print("Errors removed and variables subset.")

# ----- CALCULATE STATISTICS ---------------------------------------------------

# >>> Calculate HPMS subset statistics as table <<<
print("Calculating statistics for HPMS subset...")

# HPMS subset = HPMS data set of project area after removing errors 

summary_sub = pd.DataFrame({
    # number of road links removed
    'n_links_rm': [len(hpms) - len(hpms_sub)],

    # percentage of road links and lane miles removed
    'pcnt_links_rm': [(len(hpms) - len(hpms_sub)) / len(hpms) * 100],
    'pcnt_lnmi_rm': [(hpms['LANE_MILES'].sum() - hpms_sub['LANE_MILES'].sum()) / hpms['LANE_MILES'].sum() * 100],

    # number of road links, traffic (VMT and VKT), and lane distance (miles and kilometers) in the subset
    'n_links_sub': [len(hpms_sub)],
    'vkt_sub': [hpms_sub['VKT'].sum()],
    'vmt_sub': [hpms_sub['VMT'].sum()],
    'lnkm_sub': [hpms_sub['LANE_KMS'].sum()],
    'lnmi_sub': [hpms_sub['LANE_MILES'].sum()],

    # number and percent of road links without medium and heavy duty AADT 
    'n_na_mdv': [hpms_sub['AADT_MDV'].isna().sum()],
    'n_na_hdv': [hpms_sub['AADT_HDV'].isna().sum()],
    'pcnt_na_mdv': [hpms_sub['AADT_MDV'].isna().sum() / len(hpms_sub['AADT_MDV']) * 100],
    'pcnt_na_hdv': [hpms_sub['AADT_HDV'].isna().sum() / len(hpms_sub['AADT_HDV']) * 100],

    #percent of lane miles without medium and heavy duty AADT
    'pcnt_lnmi_na_mdv': [hpms_sub.loc[hpms_sub['AADT_MDV'].isna(), 'LANE_MILES'].sum() / hpms_sub['LANE_MILES'].sum() * 100],
    'pcnt_lnmi_na_hdv': [hpms_sub.loc[hpms_sub['AADT_HDV'].isna(), 'LANE_MILES'].sum() / hpms_sub['LANE_MILES'].sum() * 100]
})

print(summary_sub)
print("Statistics calculated for HPMS subset.")

# >>> Generate summary tables for HPMS subset grouped by classifications <<<
print("Generating summary tables for HPMS subset by groups...")

# create table of land kilometers and VKT by funtional classification

hpms_sub['VKT'] = hpms_sub['AADT'] * (hpms_sub['Shape_Length'] / 1000)
hpms_sub['VKT_MDV'] = hpms_sub['AADT_MDV'] * (hpms_sub['Shape_Length'] / 1000)
hpms_sub['VKT_HDV'] = hpms_sub['AADT_HDV'] * (hpms_sub['Shape_Length'] / 1000)
hpms_sub['VKT_LDV'] = hpms_sub['VKT'] - (hpms_sub['VKT_MDV'] + hpms_sub['VKT_HDV'])

# Group by F_SYSTEM
grouped = hpms_sub.groupby('F_SYSTEM')

# Calculate sum lane miles and lane kilometers (1 mi = 0.1609344 km)
# and sum VKT
summary_lnkm_vkt = grouped.agg(
    n=('F_SYSTEM', 'size'),
    sum_lane_mi=('LANE_MILES', 'sum'),
    sum_lane_km=('LANE_MILES', lambda x: (x * 0.1609344).sum()),
    sum_vkt=('VKT', 'sum'),
    sum_vkt_ldv=('VKT_LDV', 'sum'),
    sum_vkt_mdv=('VKT_MDV', 'sum'),
    sum_vkt_hdv=('VKT_HDV', 'sum')
).reset_index(inplace=True)

# Generate summary table of statistics by urban classification
# URBAN_DESC: urban, rural, small urban
def urban_desc(row):
    if row['URBAN'] == 0 and pd.notna(row['URBAN']):
        return 'rural'
    elif row['URBAN'] == 1 and pd.notna(row['URBAN']):
        return 'urban'
    elif row['URBAN'] == 2 and pd.notna(row['URBAN']):
        return 'small urban'
    else:
        return np.nan

hpms_sub['URBAN_DESC'] = hpms_sub.apply(urban_desc, axis=1)

# Group by urban classification and caluclate statistics
summary_urban = hpms_sub.groupby('URBAN_DESC').agg(
    n_links=('URBAN_DESC', 'count'),
    pcnt_links=('URBAN_DESC', lambda x: len(x) / len(hpms_sub) * 100),
    vkt=('VKT', 'sum'),
    pcnt_vkt=('VKT', lambda x: x.sum() / hpms_sub['VKT'].sum() * 100),
    lnkm=('LANE_KMS', 'sum'),
    pcnt_lnkm=('LANE_KMS', lambda x: x.sum() / hpms_sub['LANE_KMS'].sum() * 100),
    n_na_mdv=('AADT_MDV', lambda x: x.isna().sum()),
    n_na_hdv=('AADT_HDV', lambda x: x.isna().sum()),
    pcnt_na_mdv=('AADT_MDV', lambda x: x.isna().sum() / len(x) * 100),
    pcnt_na_hdv=('AADT_HDV', lambda x: x.isna().sum() / len(x) * 100),
    lnkm_na_mdv=('LANE_KMS', lambda x: x[hpms_sub['AADT_MDV'].isna()].sum()),
    lnkm_na_hdv=('LANE_KMS', lambda x: x[hpms_sub['AADT_HDV'].isna()].sum()),
    lnmi_na_mdv=('LANE_MILES', lambda x: x[hpms_sub['AADT_MDV'].isna()].sum()),
    lnmi_na_hdv=('LANE_MILES', lambda x: x[hpms_sub['AADT_HDV'].isna()].sum()),
    pcnt_lnkm_na_mdv=('LANE_KMS', lambda x: x[hpms_sub['AADT_MDV'].isna()].sum() / x.sum() * 100),
    pcnt_lnkm_na_hdv=('LANE_KMS', lambda x: x[hpms_sub['AADT_HDV'].isna()].sum() / x.sum() * 100)
).reset_index(inplace=True)


# Generate summary table of statistics by road functional classification
summary_fsys = hpms_sub.groupby('F_SYSTEM').agg(
    n_links=('F_SYSTEM', 'size'),
    pcnt_links=('F_SYSTEM', lambda x: len(x) / len(hpms_sub) * 100),
    vkt=('VKT', 'sum'),
    pcnt_vkt=('VKT', lambda x: x.sum() / hpms_sub['VKT'].sum() * 100),
    lnkm=('LANE_KMS', 'sum'),
    pcnt_lnkm=('LANE_KMS', lambda x: x.sum() / hpms_sub['LANE_KMS'].sum() * 100),
    n_na_mdv=('AADT_MDV', lambda x: x.isna().sum()),
    n_na_hdv=('AADT_HDV', lambda x: x.isna().sum()),
    pcnt_na_mdv=('AADT_MDV', lambda x: x.isna().sum() / len(x) * 100),
    pcnt_na_hdv=('AADT_HDV', lambda x: x.isna().sum() / len(x) * 100),
    lnkm_na_mdv=('LANE_KMS', lambda x: x[hpms_sub['AADT_MDV'].isna()].sum()),
    lnkm_na_hdv=('LANE_KMS', lambda x: x[hpms_sub['AADT_HDV'].isna()].sum()),
    lnmi_na_mdv=('LANE_MILES', lambda x: x[hpms_sub['AADT_MDV'].isna()].sum()),
    lnmi_na_hdv=('LANE_MILES', lambda x: x[hpms_sub['AADT_HDV'].isna()].sum()),
    pcnt_lnkm_na_mdv=('LANE_KMS', lambda x: x[hpms_sub['AADT_MDV'].isna()].sum() / x.sum() * 100),
    pcnt_lnkm_na_hdv=('LANE_KMS', lambda x: x[hpms_sub['AADT_HDV'].isna()].sum() / x.sum() * 100)
).reset_index(inplace=True)

# Generate summary table of statistics by state and road functional classification
summary_st_fsys = hpms_sub.groupby(['STATEFP', 'F_SYSTEM']).agg(
    n_links=('F_SYSTEM', 'size'),
    pcnt_links=('F_SYSTEM', lambda x: len(x) / len(hpms_sub) * 100),
    vkt=('VKT', 'sum'),
    pcnt_vkt=('VKT', lambda x: x.sum() / hpms_sub['VKT'].sum() * 100),
    lnkm=('LANE_KMS', 'sum'),
    pcnt_lnkm=('LANE_KMS', lambda x: x.sum() / hpms_sub['LANE_KMS'].sum() * 100),
    n_na_mdv=('AADT_MDV', lambda x: x.isna().sum()),
    n_na_hdv=('AADT_HDV', lambda x: x.isna().sum()),
    pcnt_na_mdv=('AADT_MDV', lambda x: x.isna().sum() / len(x) * 100),
    pcnt_na_hdv=('AADT_HDV', lambda x: x.isna().sum() / len(x) * 100),
    lnkm_na_mdv=('LANE_KMS', lambda x: x[hpms_sub['AADT_MDV'].isna()].sum()),
    lnkm_na_hdv=('LANE_KMS', lambda x: x[hpms_sub['AADT_HDV'].isna()].sum()),
    lnmi_na_mdv=('LANE_MILES', lambda x: x[hpms_sub['AADT_MDV'].isna()].sum()),
    lnmi_na_hdv=('LANE_MILES', lambda x: x[hpms_sub['AADT_HDV'].isna()].sum()),
    pcnt_lnkm_na_mdv=('LANE_KMS', lambda x: x[hpms_sub['AADT_MDV'].isna()].sum() / x.sum() * 100),
    pcnt_lnkm_na_hdv=('LANE_KMS', lambda x: x[hpms_sub['AADT_HDV'].isna()].sum() / x.sum() * 100)
).reset_index(inplace=True)

print("Summary tables generated for HPMS subset by groups.")

# ----- EXPORT DATA -------------------------------------------------------------
print("Exporting data...")

df = hpms_sub 
file_name = "HPMS_AADT_subset".lower()
out_dir = out_dir
my_table_export(df, file_name, out_dir)

df = summary_sub
file_name = "HPMS_AADT_subset_summary_stats".lower()
out_dir = out_dir
my_table_export(df, file_name, out_dir)

df = summary_lnkm_vkt
file_name = "HPMS_AADT_subset_summary_lane_km_vkt".lower()
out_dir = out_dir
my_table_export(df, file_name, out_dir)

df = summary_urban
file_name = "HPMS_AADT_subset_summary_by_urban".lower()
out_dir = out_dir
my_table_export(df, file_name, out_dir)

df = summary_fsys
file_name = "HPMS_AADT_subset_summary_by_fsystem".lower()
out_dir = out_dir
my_table_export(df, file_name, out_dir)

df = summary_st_fsys
file_name = "HPMS_AADT_subset_summary_by_state_fsystem".lower()
out_dir = out_dir
my_table_export(df, file_name, out_dir)

print("Data exported.")

# print total execution time calculation 
print('Total Execution time: --- %s minutes ---\n' % round(((time.time() - start_time_total)*(1/(60)))))

# ----- END OF SCRIPT ----- #
print('----- END OF SCRIPT -----')