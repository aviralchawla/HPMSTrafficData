import pandas as pd
import geopandas as gpd
from shapely import wkt
from pathlib import Path
from utils.utils import load_data

pd.set_option('display.float_format', lambda x: '%.3f' % x)

def calculate_traffic_density(df):

    print('Calculating traffic density...')

    agg_funcs = {
        'VKT': 'sum',
        'VKT_LDV': 'sum',
        'VKT_MDV': 'sum',
        'VKT_HDV': 'sum',
        'Area_Land_Orig': 'first'
    }
    grouped_df = df.groupby('GEOID20').agg(agg_funcs)

    for vehicle_type in ['VKT', 'VKT_LDV', 'VKT_MDV', 'VKT_HDV']:
        grouped_df[f'TD_{vehicle_type}'] = grouped_df[vehicle_type] / (grouped_df['Area_Land_Orig'] / 10**6)

    grouped_df = grouped_df.replace([pd.NA, pd.np.inf, -pd.np.inf], 0)

    return grouped_df.reset_index()

def main():
    TD_GDB = Path("../data/processed_data/Traffic_Density/Traffic_Density.gdb")
    HPMS_GDB = Path("../data/processed_data/HPMS/HPMS.gdb")

    intxn_gdf = load_data(TD_GDB, "density_intxn")
    intxn_gdf['geometry'] = intxn_gdf['geometry'].apply(lambda x: wkt.dumps(x))

    td_gdf = calculate_traffic_density(intxn_gdf)

    td_gdf.to_file(TD_GDB, layer="traffic_density", driver="OpenFileGDB")

