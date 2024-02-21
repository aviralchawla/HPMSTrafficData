"""

HPMS Data Project - Near-Road Exposure

Last Updated: 02/21/2023
Created by Meg Fay
University of Vermont, Burlington, VT

"""

############################## ABOUT THIS SCRIPT ##############################
#                                                                             #
# This script copies the raw HPMS and Census feature classes to a single      #
# geodatabase for cleaning the HPMS data.                                     #
#                                                                             #
############################## ABOUT THIS SCRIPT ##############################

# script title
print('''
--- Near-Road Exposure: HPMS Data Preparation ---''','\n')

# import packages 
import arcpy
import time
import datetime
import sys

# overwrite existing files (False = No, True = Yes)
arcpy.env.overwriteOutput = True
print('arcpy.env.overwriteOutput', arcpy.env.overwriteOutput,'\n')

# script to read in two geodatabases and copy selected feature classes into new geodatabase using arcpy
