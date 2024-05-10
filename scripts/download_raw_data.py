"""
<TITLE>
by Aviral Chawla, Meg Fay, Brittany Antonczak, and Gregory Rowangould

<SUMMARY>

<LICENSE>
"""

import os
import requests
import sys
from bs4 import BeautifulSoup
from pathlib import Path
import tqdm
import json

from utils.utils import *
from utils.generate_checksums import generate_checksums
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def download_hpms_data(storage_dir: Path, filename: str = "ntad_2019_hpms_raw.zip"):
    """
    Summary: Download the HPMS data and save it to the storage directory
    Inputs:
        - storage_dir (Path): Path to save the downloaded files
        - filename (str): Name of the file to save the HPMS data
    """
    print("Downloading HPMS Data ....")

    hpms_hosted_url = "https://trafficexposure.uvm.edu/download-hpms"

    download_file(hpms_hosted_url, storage_dir / filename)
    unzip_file(filename, storage_dir)

    print(f"HMPS Data downloaded and saved to {storage_dir}")


def download_census_counties_data(year: int, tiger_url: str, storage_dir: Path):
    """
    Summary: Download the Census Counties data for the given year
    Inputs:
        - year (int): Year of the Census Counties data
        - tiger_url (str): URL of the Tiger data
        - storage_dir (Path): Path to save the downloaded files
    """
    print("Downloading Census Counties Data ....")

    tiger_counties_url = f"{tiger_url}{year}/COUNTY/tl_{year}_us_county.zip"
    census_counties_storage_dir = storage_dir / "census" / "counties"

    if not census_counties_storage_dir.exists():
        census_counties_storage_dir.mkdir(parents=True)

    download_file(
        tiger_counties_url, census_counties_storage_dir / f"tl_{year}_us_county.zip"
    )
    unzip_file(f"tl_{year}_us_county.zip", census_counties_storage_dir)

    print(f"Census Counties Data downloaded and saved to {census_counties_storage_dir}")


def download_census_urban_areas_data(year: int, tiger_url: str, storage_dir: Path):
    """
    Summary: Download the Census Urban Areas data for the given year
    Inputs:
        - year (int): Year of the Census Urban Areas data
        - tiger_url (str): URL of the Tiger data
        - storage_dir (Path): Path to save the downloaded files
    """
    print("Downloading Census Urban Areas Data ....")

    tiger_urban_areas_url = f"{tiger_url}{year}/UAC/tl_{year}_us_uac10.zip"  # Note: While the data being pulled was published in 2020, it is referring to 2010 data!
    census_urban_areas_storage_dir = storage_dir / "census" / "urban_areas"

    if not census_urban_areas_storage_dir.exists():
        census_urban_areas_storage_dir.mkdir(parents=True)

    download_file(
        tiger_urban_areas_url,
        census_urban_areas_storage_dir / f"tl_{year}_us_uac10.zip",
    )
    unzip_file(f"tl_{year}_us_uac10.zip", census_urban_areas_storage_dir)

    print(
        f"Census Urban Areas Data downloaded and saved to {census_urban_areas_storage_dir}"
    )


def download_census_blocks_data(year: int, tiger_url: str, storage_dir: Path):
    """
    Summary: Download the Census Blocks data for the given year
    Inputs:
        - year (int): Year of the Census Blocks data
        - tiger_url (str): URL of the Tiger data
        - storage_dir (Path): Path to save the downloaded files
    """
    print("Downloading Census Blocks Data ....")

    tiger_blocks_url = f"{tiger_url}{year}/TABBLOCK/"

    census_blocks_storage_dir = storage_dir / "census" / "blocks"
    if not census_blocks_storage_dir.exists():
        census_blocks_storage_dir.mkdir(parents=True)

    try:
        res = requests.get(tiger_blocks_url)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error occurred during HTTP request: {e}")
        sys.exit(1)

    soup = BeautifulSoup(res.content, "html.parser")

    links = []
    for link in soup.find_all("a"):
        links.append(link.get("href"))

    census_data = [link for link in links if str(link).endswith(".zip")]

    for state in tqdm.tqdm(census_data):
        data_url = f"{tiger_blocks_url}{state}"
        download_file(data_url, census_blocks_storage_dir / state)

    print("Unzipping files ...")
    # Unzip and delete .zip files
    for file in tqdm.tqdm(os.listdir(census_blocks_storage_dir)):
        unzip_file(file, census_blocks_storage_dir)

    print(f"Census Blocks Data downloaded and saved to {census_blocks_storage_dir}")


def verify_download(dir: str):
    """
    Summary: Verify the checksums of the downloaded files
    Inputs:
        - checksums_path (Path): Path to the checksums file
    """
    checksums_path = Path(f"../data/checksums_{dir}.json")

    with open(checksums_path, "r") as f:
        checksums = json.load(f)

    for file, checksum in tqdm.tqdm(checksums.items()):
        if generate_checksums(file) != checksum:
            print(f"Checksums do not match for {file}")
            file_ok = False

            break
        else:
            file_ok = True

    if file_ok:
        print(f"{dir}: Ok")


def main():

    # Prepare storage directory
    STORAGE_DIR = Path("../data/raw_data")

    if not STORAGE_DIR.exists():
        STORAGE_DIR.mkdir(parents=True)

    TIGER_URL = "https://www2.census.gov/geo/tiger/TIGER"
    SHAPEFILE_YEAR = 2020

    hpms_filename = "ntad_2019_hpms_raw.zip"
    download_hpms_data(STORAGE_DIR, filename=hpms_filename)

    download_census_counties_data(SHAPEFILE_YEAR, TIGER_URL, STORAGE_DIR)

    download_census_urban_areas_data(SHAPEFILE_YEAR, TIGER_URL, STORAGE_DIR)

    download_census_blocks_data(SHAPEFILE_YEAR, TIGER_URL, STORAGE_DIR)

    print("Verifying downloaded files ...")
    # Verify the downloaded files
    for dir in ["ntad_2019_hpms_raw", "counties", "urban_areas", "blocks"]:
        verify_download(dir)


if __name__ == "__main__":
    main()
