import pandas as pd
import geopandas as gpd
import os
from shapely import wkt
from pathlib import Path

# Suppress scientific notation in pandas
pd.set_option('display.float_format', lambda x: '%.3f' % x)

# Check file paths exist (Example paths, update as necessary)
intxn_gdb_path = Path("..")
hpms_path = Path("..")
main_out_dir = Path("..")

# Ensure output directory exists
main_out_dir.mkdir(parents=True, exist_ok=True)

def load_intxn_data(gdb_path, feature_class_name):
    # Load intersection data from a geodatabase
    intxn_gdf = gpd.read_file(gdb_path, layer=feature_class_name)
    
    # Convert geometry to WKT
    intxn_gdf['geometry'] = intxn_gdf['geometry'].apply(lambda x: wkt.dumps(x))
    
    return intxn_gdf

# Function to calculate traffic density by census block
def calculate_traffic_density(df):
    
    # Aggregate by GEOID20
    agg_funcs = {
        'VKT': 'sum',
        'VKT_LDV': 'sum',
        'VKT_MDV': 'sum',
        'VKT_HDV': 'sum',
        'Area_Land_Orig': 'first'  # Assuming Area_Land_Orig is constant per GEOID20
    }
    grouped_df = df.groupby('GEOID20').agg(agg_funcs)
    
    # Calculate traffic density (VKT/km2)
    for vehicle_type in ['VKT', 'VKT_LDV', 'VKT_MDV', 'VKT_HDV']:
        grouped_df[f'TD_{vehicle_type}'] = grouped_df[vehicle_type] / (grouped_df['Area_Land_Orig'] / 10**6)
    
    # Replace NaN and inf values with 0
    grouped_df = grouped_df.replace([pd.NA, pd.np.inf, -pd.np.inf], 0)
    
    return grouped_df.reset_index()

if __name__ == "__main__":
    # Adjust the function as necessary to match your data format
    intxn_data = load_intxn_data(intxn_gdb_path, "your_intersection_feature_class_name")

    # Load HPMS traffic volume data
    hpms_data = pd.read_csv(hpms_path, dtype={'STATEFP': str, 'COUNTYFP': str, 'GEOID20': str})

    # Join data
    combined_data = pd.merge(intxn_data, hpms_data, on="FID_Link_Cnty_Intxn")

    # Calculate traffic density by vehicle type (VKT/km2)
    traffic_density = calculate_traffic_density(combined_data)

    # Export data to CSV
    output_file_path = main_out_dir / "US_Census_Block_Traffic_Density_Calculations.csv"
    traffic_density.to_csv(output_file_path, index=False)
    print(f"Data exported to {output_file_path}")
