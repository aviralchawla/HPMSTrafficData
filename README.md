# HPMS Data Processing (Transportation Research Center)

## Overview
This repository contains the scripts used to process the HPMS data for the Near Road Exposure project. The scripts are organized in a pipeline fashion, where each script is responsible for a specific task.

### Repository Structure
The repository is organized as follows:

## Get Started
To get started with this project, you need to follow the following steps:
1. Initialize your ArcPy environment as `arcpy-hpms`.
2. `conda activate arcpy-hpms`
3. `powershell -File 'setup.ps1'`

## Data Source
The data used in this project is the HPMS data, which is available at the [??](). The data is available in the form of a geodatabase file, which are organized by state and year.

## Methodology
The methodology used in this project is as follows:

## Usage
To run the scripts, you need to have the following dependencies installed:

## Contributing
To contribute to this project, you need to follow the following steps:

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgements
This project is supported by the Transportation Research Center at the University of Vermont.

### Order of the scripts [Main Pipeline]
1. ~~download_raw_data d.py (1)~~
2. ~~HPMS_organize_gdb.py (2)~~
3. ~~HPMS_data_preparation.pu (2)~~
4. ~~NearRoadExp_AADT_Subset.py (2)~~
5. ~~aadt_imputation.py (3)~~
6. ~~JoinGeometry_HPMS_AADT_imputation.py (3)~~
7. ~~vmt_calc.py (3)~~
9. TD_organize_gdb.py (4)
10. TD_data_preparation.py (4)
11. estimate_td.py (4)

### To-Dos:
- Merge the scripts
- Prepare raw data script
- Section the TD_organize in states instead of nation-wide
- Data EDA
- Create unit tests for all the scripts
