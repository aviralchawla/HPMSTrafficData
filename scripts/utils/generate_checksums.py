import hashlib
from pathlib import Path
import os
import json
import tqdm

def generate_checksums(file_path):
    with open(file_path, 'rb') as file:
        file_content = file.read()
    checksum =  hashlib.sha256(file_content).hexdigest()
    return checksum

def get_all_files(directory):
    files = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            files.append(os.path.join(dirpath, filename))
    return files

def main():

    RAW_DATA_DIR = Path("../../data/raw_data")

    HPMS_DIR = RAW_DATA_DIR / 'ntad_2019_hpms_raw'
    CENSUS_COUNTIES_DIR = RAW_DATA_DIR / 'census' / 'counties'
    CENSUS_URBAN_AREAS_DIR = RAW_DATA_DIR / 'census' / 'urban_areas'
    CENSUS_BLOCKS_DIR = RAW_DATA_DIR / 'census' / 'blocks'

    for DATA_DIR in [HPMS_DIR, CENSUS_COUNTIES_DIR, CENSUS_URBAN_AREAS_DIR, CENSUS_BLOCKS_DIR]:

        files = get_all_files(DATA_DIR)

        print(f"Generating checksums for {str(DATA_DIR).split('/')[-1]}...")

        checksums = {}
        for file in tqdm.tqdm(files):
            checksum = generate_checksums(file)
            checksums[file[3:]] = checksum
        
        with open(Path(f'../../data/checksums_{str(DATA_DIR).split('/')[-1]}.json'), 'w') as f:
            json.dump(checksums, f)


