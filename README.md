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
The data used in this project is the Highway Performance Monitoring System (HPMS) data, which, in its most recent version is available at the USDOT Bureau of Transportation Statistics (https://geodata.bts.gov/datasets/c199f2799b724ffbacf4cafe3ee03e55/about). The data used in this project (HPMS 2018) is available in the form of a geodatabase file organized by state and year.

## Methodology
The methodology used in this project is as follows:

# Raw Data
python download_raw_data.py <br>
python compile_raw_data.py <br>

# HPMS
python subset_hpms.py <br>
python impute_hpms.py <br>
python joingeo_hpms.py <br>

# Traffic Density
python compile_traffic_density.py <br>

## Usage
To run the scripts, you need to have the following dependencies installed:

## Contributing
To contribute to this project, you need to follow the following steps:

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgements
This project is supported by the Transportation Research Center at the University of Vermont.

