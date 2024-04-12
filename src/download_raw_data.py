#### Script to download and unpack all the raw data from the Census Bureau and HPMS DOT data ####
#### Storage Requirement: GB; Memory Requirement: GB ####

import os
import requests
import sys
import zipfile
from bs4 import BeautifulSoup
from pathlib import Path
import tqdm

def download_file(url, storage_dir):
    try:
        res = requests.get(url, stream=True, verify=False)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error occurred during HTTP request: {e}")
        sys.exit(1)
    
    with open(storage_dir, 'wb') as f:
        f.write(res.content)

def unzip_file(file, storage_dir):
    with zipfile.ZipFile(storage_dir / file, 'r') as zip_ref:
        zip_ref.extractall(storage_dir / file.split('.')[0])
    os.remove(storage_dir / file)

def download_census_data(year, storage_dir):
    tiger_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TABBLOCK/"
    
    HPMS_STORAGE_DIR = storage_dir / 'census'
    if not HPMS_STORAGE_DIR.exists():
        HPMS_STORAGE_DIR.mkdir(parents=True)

    try:
        res = requests.get(tiger_url)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error occurred during HTTP request: {e}")
        sys.exit(1)

    soup = BeautifulSoup(res.content, 'html.parser')

    links = []
    for link in soup.find_all('a'):
        links.append(link.get('href'))

    census_data = [link for link in links if str(link).endswith('.zip')]
    print("Downloading Census Data")

    for state in tqdm.tqdm(census_data):
        data_url = f"{tiger_url}{state}"
        download_file(data_url, HPMS_STORAGE_DIR / state)

    print("Download complete")

    # Unzip and delete .zip files
    print("Unzipping files")

    for file in tqdm.tqdm(os.listdir(storage_dir / 'census')):
        unzip_file(file, storage_dir / 'census')

def download_hpms_data(storage_dir):
    hpms_hosted_url = "https://trafficexposure.uvm.edu/download-hpms"

    print('Downloading HPMS Data')
    download_file(hpms_hosted_url, storage_dir / 'ntad_2019_hpms_raw.zip')
    unzip_file('ntad_2019_hpms_raw.zip', storage_dir)


def main():

    # Prepare storage file
    STORAGE_DIR = Path("../data/raw_data")

    if not STORAGE_DIR.exists():
        STORAGE_DIR.mkdir(parents=True)
    
    # Download HPMS Data
    download_hpms_data(STORAGE_DIR)

    # Download Census Data
    HPMS_YEAR = 2018
    download_census_data(HPMS_YEAR, STORAGE_DIR)


if __name__ == "__main__":
    main()