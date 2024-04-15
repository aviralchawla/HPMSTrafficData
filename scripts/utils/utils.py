from pathlib import Path
import requests
import sys
import zipfile
import fiona
import os

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

def shapefile_to_geodatabase(shapefile: Path, geodatabase: Path, layer: str):
    '''
    Summary: Convert the shapefile to a geodatabase
    Inputs:
        - shapefile (Path): Path to the shapefile
        - geodatabase (Path): Path to save the geodatabase
        - layer (str): Name of the layer in the geodatabase
    '''
    with fiona.open(shapefile) as source:
        crs = source.crs
        schema = source.schema
    
    with fiona.open(geodatabase, 'w', driver='OpenFileGDB', crs=crs, schema=schema, layer=layer) as sink:
        for feature in fiona.open(shapefile):
            sink.write(feature)