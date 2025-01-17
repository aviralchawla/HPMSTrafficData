# HPMS Traffic Data (Transportation Research Center)

## Overview
This repository contains the scripts used to process the HPMS data for Estimating High-Resolution National Traffic Data by Vehicle Class: A Machine Learning Approach. The scripts are organized in a pipeline fashion, where each script is responsible for a specific task.

## About the Project 
The Highway Performance Monitoring System, managed by the Federal Highway Administration, provides essential data on average annual daily traffic across U.S. roadways. Still, it has limited representation of medium- and heavy-duty vehicles on non-interstate roads. This gap limits research and policy analysis on the impacts of truck traffic, especially concerning air quality and public health. To address this, we apply random forest regression to estimate medium- and heavy-duty vehicle volumes in areas with sparse data, improving upon earlier approaches such as linear regression. This results in a more comprehensive dataset, which enables the estimation of traffic density at the census block level as a proxy for traffic-related air pollution exposure. Our high-resolution spatial data products, rigorously validated, provide a more accurate representation of truck traffic and its environmental and health impacts. These datasets are valuable for transportation planning, public health research, and policy decisions aimed at mitigating the effects of truck traffic on vulnerable communities exposed to air pollution.

### Repository Structure
The repository is organized as follows:

## Get Started
To get started with this project, you need to follow the following steps: <br>
1. Initialize your ArcPy environment as `arcpy-hpms`. <br>
2. `conda activate arcpy-hpms` <br>
3. `powershell -File 'setup.ps1'` <br>

## Data Source
The data used in this project is the Highway Performance Monitoring System (HPMS) data, which, in its most recent version is available at the USDOT Bureau of Transportation Statistics (https://geodata.bts.gov/datasets/c199f2799b724ffbacf4cafe3ee03e55/about). The data used in this project (HPMS 2018) is available in the form of a geodatabase file organized by state and year.

## Methodology
Please see manuscript, currently in preprint at: INSERT LINK

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

