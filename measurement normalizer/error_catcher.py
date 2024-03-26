# Commandline scriptrun: cd Users/Tecan/Documents/GitHub/automation-Tecan-Fluent/measurement normalizer/error_catcher.py
# The following script is a truncated version of the backdilution cherrypick generator, meant to warn users about normalization failures prior to backdilution.

# Import all the things
import os
from datetime import datetime
import math as math
import pandas as pd
import numpy as np

# Take user input from the Fluent's ExportFile command.
#export_filepath = "G:/.shortcut-targets-by-id/1SA9d7OhoYdnH2QPxGxtxoE_0ZB5ZlyCP/RnD Transfer/Byonoy/measurement normalizer/meas_and_norm_user_inputs.csv" 
export_filepath = "C:/Users/Tecan/Desktop/Tecan Fluent780 desktop files/measurement_and_normalization/meas_and_norm_user_inputs.csv"
user_inputs = pd.read_csv(export_filepath, header=None)
normalization_target = float(user_inputs.iloc[1,0])
starting_sample_vol = float(user_inputs.iloc[1,1])
target_vol = float(user_inputs.iloc[1,2])

# Make a column for well IDs in a 96w plate (arranged columnwise)
plate_96_rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
plate_96_columns = [str(num) for num in range(1, 13)]
plate_96_wells = [row + column for column in plate_96_columns for row in plate_96_rows]

# Pull in a byonoy measurement file.
byonoy_measurement_filepath_export = "C:/Users/Tecan/Desktop/Tecan Fluent780 desktop files/measurement_and_normalization/byonoy_measurement_filepath.csv"
measurement_filepath = str(pd.read_csv(byonoy_measurement_filepath_export, header=None).iloc[1,0])
df = pd.read_csv(measurement_filepath, header=None)
columnwise_od_strings = list(pd.melt(df.iloc[1:9, 1:13], var_name = "column", value_name = "od")["od"])
columnwise_od_values = [float(val) for val in columnwise_od_strings]

# Build the metadata dataframe
norm_target_list = [normalization_target for val in range(0,len(columnwise_od_values))]
sample_cp_volumes = [round((normalization_target*target_vol/od),1) for od in columnwise_od_values]
remaining_sample_volumes = [round((starting_sample_vol-val),1) for val in sample_cp_volumes]
diluent_cp_volumes = [round((target_vol-vol),1) for vol in sample_cp_volumes]
total_vols = [sample_cp_volumes[each] + diluent_cp_volumes[each] for each in range(0,len(columnwise_od_values))]

metadata_df = pd.DataFrame({
    'well id' : plate_96_wells,
    'measured od' : columnwise_od_values,
    'target od' : norm_target_list,
    'sample volume for backdilution' : sample_cp_volumes,
    'remaining sample volume' : remaining_sample_volumes,
    'diluent volume for backdilution' : diluent_cp_volumes,
    'diluted sample volume' : total_vols
})

# Error handling for inputs where final OD cannot be acheived.
metadata_neg_value_error_df = metadata_df[(metadata_df['remaining sample volume'] <= 0)]
if len(metadata_neg_value_error_df) > 0:
    toggle = 1
else:
    toggle = 0
warning_df = pd.DataFrame({
    'errorWarningToggle' : [toggle]
})

#local_filepath = "C:/Users/Max/Desktop/meas_and_norm_testing/"
local_filepath = "C:/Users/Tecan/Desktop/Tecan Fluent780 desktop files/measurement_and_normalization/"
warning_df.to_csv(local_filepath+"errorWarningToggle.csv", index=False)