from pathlib import Path
import requests
import sys
import zipfile
import fiona
import os
import geopandas as gpd

def download_file(url: str, storage_dir: Path):
    '''
    Summary: Download file from the given URL and save it to the storage directory
    Inputs: 
        - url (str): URL of the file to download 
        - storage_dir (Path): Path to save the downloaded file
    '''
    try:
        res = requests.get(url, stream=True, verify=False)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error occurred during HTTP request: {e}")
        sys.exit(1)
    
    with open(storage_dir, 'wb') as f:
        f.write(res.content)

def unzip_file(file: str, storage_dir: Path):
    '''
    Summary: Extract the contents of the zip file to the storage directory
    Inputs:
        - file (str): Name of the zip file to extract
        - storage_dir (Path): Path to save the extracted files
    '''
    with zipfile.ZipFile(storage_dir / file, 'r') as zip_ref:
        zip_ref.extractall(storage_dir / file.split('.')[0])
    os.remove(storage_dir / file)

def shp_to_gdb(input_shp: Path, output_gdb: Path, layer_name: str):
    '''
    Summary: Convert shapefile to file geodatabase
    Inputs:
        - input_shp (Path): Path to the shapefile
        - output_gdb (Path): Path to the output file geodatabase
        - layer_name (str): Name of the layer in the file geodatabase
    Output:
        - File geodatabase with the converted shapefile
    '''
    layer = gpd.read_file(input_shp, engine="pyogrio", use_arrow=True)
    layer.to_file(output_gdb, layer=layer_name, driver='OpenFileGDB')

def get_state_fips(blocks_dir: Path):
    '''
    Summary: Get the state FIPS codes from the directory names
    Inputs:
        - blocks_dir (Path): Path to the directory containing the Census Blocks data
    Output:
        - state_fips (list): List of state FIPS codes
    '''
    
    all_dirs = os.listdir(blocks_dir)
    state_fips = [f.split('_')[2] for f in all_dirs]

    return state_fips