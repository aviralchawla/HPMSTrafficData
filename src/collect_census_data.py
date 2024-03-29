import requests
import geopandas as gpd
from bs4 import BeautifulSoup

YEAR = 2018

tiger_url = f"https://www2.census.gov/geo/tiger/TIGER{YEAR}/TABBLOCK/"

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

for state in census_data:
    print(f"Downloading {state}")
    data_url = f"{tiger_url}{state}"
    try:
        res = requests.get(data_url)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error occurred during HTTP request: {e}")
        sys.exit(1)

    with open(f"../data/census_blocks_{YEAR}/{state}", 'wb') as f:
        f.write(res.content)

    print(f"Downloaded {state}")

print("Download complete")

# unzip all files
import os
import zipfile

for file in os.listdir(f"../data/census_blocks_{YEAR}"):
    with zipfile.ZipFile(f"../data/census_blocks_{YEAR}/{file}", 'r') as zip_ref:
        zip_ref.extractall(f"../data/census_blocks_{YEAR}")
    print(f"Unzipped {file}")

print("Unzip complete")

# merge all the shp files into one gdb
import fiona
import fiona.crs

gdb = f"../data/census_blocks_{YEAR}/census_blocks_{YEAR}.gdb"
if not os.path.exists(gdb):
    os.makedirs(gdb)

shp_files = [f"../data/census_blocks_{YEAR}/{file}" for file in os.listdir(f"../data/census_blocks_{YEAR}") if file.endswith('.shp')]

for shp in shp_files:
    gdf = gpd.read_file(shp)
    gdf.to_file(gdb, driver='FileGDB', layer=f"census_blocks_{YEAR}", crs=gdf.crs)
    print(f"Added {shp} to gdb")

print("Merge complete")

