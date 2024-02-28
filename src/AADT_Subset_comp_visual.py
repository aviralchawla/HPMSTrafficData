
"""

HPMS Data Project - Near-Road Exposure

Last Updated: 02/28/2023
Created by Meg Fay
University of Vermont, Burlington, VT

"""
# script title
print('''--- Near-Road Exposure: HPMS Subset Comparison ---''','\n')

# Import required libraries
import pandas as pd
import matplotlib.pyplot as plt

# Print script title
print("--- Near-Road Exposure: HPMS Subset Comparison Visuals ---\n\n")

# ----- SET LOCAL VARIABLES ---------------------------------------------------

# file paths to AADT subset statistics (from GUI and R script)
R_file_path = "Y:/EDF_Near Road Exposure/UPDATED ANALYSIS/TRD Validation - 2024/AADT Estimation/County Analysis/HPMS Dataset"

# file paths to AADT subset statistics (from arcpy and python script)
py_file_path = "Z:/ROAD_AQ/HPMS Traffic Data/HPMS/AADT Subset/HPMS Dataset"

# output folder path
output_folder_path = "Z:/ROAD_AQ/HPMS Traffic Data/HPMS/AADT Subset/HPMS Comparison"

# ----- LOAD DATA -------------------------------------------------------------
# Load data from R and Python
R_data = pd.read_csv(f"{R_file_path}/hpms_aadt_subset_summary_by_state_fsystem.csv")
py_data = pd.read_csv(f"{py_file_path}/hpms_aadt_subset_summary_by_state_fsystem.csv")

# ----- DATA PROCESSING -------------------------------------------------------

# Sort data by state and functional system
R_data = R_data.sort_values(by=['STATEFP', 'F_SYSTEM'])
py_data = py_data.sort_values(by=['STATEFP', 'F_SYSTEM'])

# Find rows in py_data that aren't in R_data
py_unique_rows = py_data[~py_data[['STATEFP', 'F_SYSTEM']].apply(tuple,1).isin(R_data[['STATEFP', 'F_SYSTEM']].apply(tuple,1))]
print("Python unique rows:  \n", py_unique_rows)
# All unique python rows are empty

# Find rows in R_data that aren't in py_data
R_unique_rows = R_data[~R_data[['STATEFP', 'F_SYSTEM']].apply(tuple,1).isin(py_data[['STATEFP', 'F_SYSTEM']].apply(tuple,1))]
print("R unique rows:  \n", R_unique_rows)
# There are no unique rows in R_data

# Find differences between R and Python data
diff = R_data - py_data
print("Differences between R and Python data:  \n", diff)

# Remove rows in py_data that aren't in R_data
py_data = py_data[py_data[['STATEFP', 'F_SYSTEM']].apply(tuple,1).isin(R_data[['STATEFP', 'F_SYSTEM']].apply(tuple,1))]

# ----- DATA PLOTTING -------------------------------------------------------

# Get unique functional systems
functional_systems = R_data['F_SYSTEM'].unique()

# create scatterplot plot of differences in n_links between R and Python data

# Create a scatter plot for each functional system
for fs in functional_systems:
    subset_R_data = R_data[R_data['F_SYSTEM'] == fs]
    subset_py_data = py_data[py_data['F_SYSTEM'] == fs]
    plt.scatter(subset_R_data['n_links'], subset_py_data['n_links'], label=fs)


plt.legend(title='Functional System')
plt.xlabel('R Data')
plt.ylabel('Python Data')
plt.title('Number of Links: R vs Python')

plt.show()

#create a scatterplot of differences in vkt between R and Python data

for fs in functional_systems:
    subset_R_data = R_data[R_data['F_SYSTEM'] == fs]
    subset_py_data = py_data[py_data['F_SYSTEM'] == fs]
    plt.scatter(subset_R_data['vkt'], subset_py_data['vkt'], label=fs)

plt.legend(title='Functional System')
plt.xlabel('R Data')
plt.ylabel('Python Data')
plt.title('Vehicle Kilometers Traveled: R vs Python')

plt.show()

# create a bar plot of total percent differences in each variable between R and Python data
sum_diff = diff.sum()
sum_diff_percent = (sum_diff / R_data.sum()) * 100
sum_diff_percent.plot(kind='bar')
plt.xlabel('Variable')
plt.ylabel('Percent Difference')
plt.title('Total Percent Difference in Variables: R vs Python')
plt.show()



