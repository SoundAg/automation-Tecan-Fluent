# To run: cd C:/Users/Tecan/Documents/Github/automation-Tecan-Fluent/RNAP_backdilution_cherrypick_csv_generator_DEPLOYED.py
# UPDATED as of: 03/15/2024

import csv
import os
from datetime import datetime
import math as math
import pandas as pd
import numpy as np


# Step 1: Declare all filepaths to be used in the script.
exported_variables_file_path = "C:/Users/Tecan/Desktop/Tecan Fluent desktop files/RNAP data management/rnap_automated_backdilution_cherrypick_inputs.csv"
spark_filepaths = "G:/.shortcut-targets-by-id/1V3zHAt-KtgEHOLBdDqNfpfAGsRY6myLO/Automation/Tecan Fluent resources/Cherrypicks/Cherrypick optimizer/RNAP optimizer/rnap_spark_filepaths.csv"
local_working_directory = "C:/Users/Tecan/Desktop/Tecan Fluent desktop files/RNAP data management/working directory/"
local_storage_directory = "C:/Users/Tecan/Desktop/Tecan Fluent desktop files/RNAP data management/automated backdilution cherrypick logs/"
gdrive_cherrypick_storage_directory = "G:/.shortcut-targets-by-id/1SA9d7OhoYdnH2QPxGxtxoE_0ZB5ZlyCP/RnD Transfer/Fluent 1080/RNA Prep Data/Backdilution cherrypick log/"
gdrive_metadata_storage_directory = "G:/.shortcut-targets-by-id/1SA9d7OhoYdnH2QPxGxtxoE_0ZB5ZlyCP/RnD Transfer/Fluent 1080/RNA Prep Data/Backdilution metadata log/"

# Load the exported CSV file containing runtime variables into a DataFrame.
df = pd.read_csv(exported_variables_file_path ,header=None)
source_plate_count, norm_conc_1, norm_conc_2, norm_conc_3, norm_conc_4, elution_volume_1, elution_volume_2, elution_volume_3, elution_volume_4 = df.iloc[1, :].astype(float)
source_plate_count = int(source_plate_count)

# Step 2: Make a list of filepaths for all selected Spark measurements, specified at runtime.
spark_filepath_df = pd.read_csv(spark_filepaths ,header=None)
standards_filepath = spark_filepath_df.iloc[1,0]
plate1_filepath = spark_filepath_df.iloc[1,1]
plate2_filepath = spark_filepath_df.iloc[1,2]
plate3_filepath = spark_filepath_df.iloc[1,3]
plate4_filepath = spark_filepath_df.iloc[1,4]
selected_measurement_filepaths = [standards_filepath, plate1_filepath, plate2_filepath, plate3_filepath, plate4_filepath][0:source_plate_count+1]

# Step 4: Process Standards data from the Ecoli rRNA standards assay plate.
standards_df = pd.read_excel(standards_filepath)
standards_extracted_data = standards_df.iloc[53:61, 1:13].values.astype(float)
standards_transposed = standards_extracted_data.T
standards_0 = [standards_transposed[each][0] for each in range(0,12)]
standards_5 = [standards_transposed[each][1] for each in range(0,12)]
standards_10 = [standards_transposed[each][2] for each in range(0,12)]
standards_20 = [standards_transposed[each][3] for each in range(0,12)]
standards_40 = [standards_transposed[each][4] for each in range(0,12)]
standards_60 = [standards_transposed[each][5] for each in range(0,12)]
standards_80 = [standards_transposed[each][6] for each in range(0,12)]
standards_100 = [standards_transposed[each][7] for each in range(0,12)]
all_standards_rfu_values = standards_0 + standards_5 + standards_10 + standards_20 + standards_40 + standards_60 + standards_80 + standards_100

standards_concentrations = [0.0, 5.0, 10.0, 20.0, 40.0, 60.0, 80.0, 100.0]
standards_concentrations_array = []
for each in range(0,len(standards_concentrations)):
    for n in range(0,12):
        standards_concentrations_array.append(standards_concentrations[each])
        
slope, y_intercept = np.polyfit(all_standards_rfu_values, standards_concentrations_array, 1)

# Step 6: Process Spark RNA Quant excel files containing sample measurement data.
plate_96_rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
plate_96_columns = [str(num) for num in range(1, 13)]
plate_96_wells = [row + column for column in plate_96_columns for row in plate_96_rows]

filename_list, well_id_list, elution_plate_id_list, backdilution_plate_id_list, elution_volume_list, eluted_sample_volume_list = [],[],[],[],[],[]
rfu_data_list_1, rfu_data_list_2, rfu_data_list_3, rfu_data_list_4 = [],[],[],[]
calculated_rna_conc_list_1, calculated_rna_conc_list_2, calculated_rna_conc_list_3, calculated_rna_conc_list_4 = [],[],[],[]
backdilution_volume_list_1, backdilution_volume_list_2, backdilution_volume_list_3, backdilution_volume_list_4 = [],[],[],[]
backdiluted_conc_1, backdiluted_conc_2, backdiluted_conc_3, backdiluted_conc_4 = [],[],[],[]
backdiluted_sample_total_volume_1, backdiluted_sample_total_volume_2, backdiluted_sample_total_volume_3, backdiluted_sample_total_volume_4 = [],[],[],[]

only_measurement_filepaths = selected_measurement_filepaths[1:]
for loop_count, excel_filepath in enumerate(only_measurement_filepaths, start=1):
    elution_plate_id = f'Elution plate[00{loop_count}]'
    backdilution_plate_id = f'Backdilution plate[00{loop_count}]'
    normalization_concentration = locals()[f'norm_conc_{loop_count}']
    elution_volume = locals()[f'elution_volume_{loop_count}']
    #rna_transfer_volume = elution_volume / 4
    rna_transfer_volume = 10
    
    df = pd.read_excel(excel_filepath)
    extracted_data = df.iloc[53:61, 1:13].values
    transposed_data = extracted_data.T

    if loop_count == 1:
        rfu_data_list_1 = [float(val) for sublist in transposed_data for val in sublist]
        calculated_rna_conc_list_1 = [((val * slope * 2) + y_intercept) for val in rfu_data_list_1]
        backdilution_volume_list_1 = [round(((rna_transfer_volume * conc / normalization_concentration) - rna_transfer_volume), 1) if conc > normalization_concentration else 0.0 for conc in calculated_rna_conc_list_1]
        backdiluted_sample_total_volume_1 = [volume + rna_transfer_volume for volume in backdilution_volume_list_1]
        for each in range(0,len(calculated_rna_conc_list_1)):
            backdiluted_conc = round((calculated_rna_conc_list_1[each] * rna_transfer_volume)/(rna_transfer_volume + backdilution_volume_list_1[each]), 1)
            backdiluted_conc_1.append(backdiluted_conc)
    if loop_count == 2: 
        rfu_data_list_2 = [float(val) for sublist in transposed_data for val in sublist]
        calculated_rna_conc_list_2 = [((val * slope * 2) + y_intercept) for val in rfu_data_list_2]
        backdilution_volume_list_2 = [round(((rna_transfer_volume * conc / normalization_concentration) - rna_transfer_volume), 1) if conc > normalization_concentration else 0.0 for conc in calculated_rna_conc_list_2]
        backdiluted_sample_total_volume_2 = [volume + rna_transfer_volume for volume in backdilution_volume_list_2]
        for each in range(0,len(calculated_rna_conc_list_2)):
            backdiluted_conc = round((calculated_rna_conc_list_2[each] * rna_transfer_volume)/(rna_transfer_volume + backdilution_volume_list_2[each]), 1)
            backdiluted_conc_2.append(backdiluted_conc)
    if loop_count == 3: 
        rfu_data_list_3 = [float(val) for sublist in transposed_data for val in sublist]
        calculated_rna_conc_list_3 = [((val * slope * 2) + y_intercept) for val in rfu_data_list_3]
        backdilution_volume_list_3 = [round(((rna_transfer_volume * conc / normalization_concentration) - rna_transfer_volume), 1) if conc > normalization_concentration else 0.0 for conc in calculated_rna_conc_list_3]
        backdiluted_sample_total_volume_3 = [volume + rna_transfer_volume for volume in backdilution_volume_list_3]
        for each in range(0,len(calculated_rna_conc_list_3)):
            backdiluted_conc = round((calculated_rna_conc_list_3[each] * rna_transfer_volume)/(rna_transfer_volume + backdilution_volume_list_3[each]), 1)
            backdiluted_conc_3.append(backdiluted_conc)   
    if loop_count == 4: 
        rfu_data_list_4 = [float(val) for sublist in transposed_data for val in sublist]
        calculated_rna_conc_list_4 = [((val * slope * 2) + y_intercept) for val in rfu_data_list_4]
        backdilution_volume_list_4 = [round(((rna_transfer_volume * conc / normalization_concentration) - rna_transfer_volume), 1) if conc > normalization_concentration else 0.0 for conc in calculated_rna_conc_list_4]
        backdiluted_sample_total_volume_4 = [volume + rna_transfer_volume for volume in backdilution_volume_list_4]
        for each in range(0,len(calculated_rna_conc_list_4)):
            backdiluted_conc = round((calculated_rna_conc_list_4[each] * rna_transfer_volume)/(rna_transfer_volume + backdilution_volume_list_4[each]), 1)
            backdiluted_conc_4.append(backdiluted_conc)
            
    num_values = 96
    filename_list.extend([os.path.basename(excel_filepath)] * num_values)
    well_id_list.extend(plate_96_wells[:num_values])
    elution_plate_id_list.extend([elution_plate_id] * num_values)
    backdilution_plate_id_list.extend([backdilution_plate_id] * num_values)
    elution_volume_list.extend([elution_volume] * num_values)
    eluted_sample_volume_list.extend([elution_volume-rna_transfer_volume] * num_values)
    
rfu_data_list = rfu_data_list_1 + rfu_data_list_2 + rfu_data_list_3 + rfu_data_list_4
calculated_rna_conc_list = calculated_rna_conc_list_1 + calculated_rna_conc_list_2 + calculated_rna_conc_list_3 + calculated_rna_conc_list_4
rna_yield_list = [calculated_rna_conc_list[n] * elution_volume_list[n] for n in range(len(calculated_rna_conc_list))]
backdilution_volume_list = backdilution_volume_list_1 + backdilution_volume_list_2 + backdilution_volume_list_3 + backdilution_volume_list_4
backdiluted_conc = backdiluted_conc_1 + backdiluted_conc_2 + backdiluted_conc_3 + backdiluted_conc_4
backdiluted_sample_total_volume_list = backdiluted_sample_total_volume_1 + backdiluted_sample_total_volume_2 + backdiluted_sample_total_volume_3 + backdiluted_sample_total_volume_4

# Step 7: Merge all data lists into dataframes, then export as metadata/cherrypick csv files for automated cherrypick file generation. 

metadata_df = pd.DataFrame({
    'Measurement file name': filename_list,
    'Well ID': well_id_list,
    'RNA Elution Plate #': elution_plate_id_list,
    'RFU': rfu_data_list,
    'Eluted RNA conc (ng/ul)': calculated_rna_conc_list,
    'RNA extraction yield (ng)' : rna_yield_list,
    'Elution volume' : elution_volume_list,
    'Elution sample remaining volume (ul)' : eluted_sample_volume_list,   
    'Backdilution Plate #': backdilution_plate_id_list,
    'Backdilution volume needed for normalization (ul)': backdilution_volume_list,
    'Backdiluted RNA conc (ng/ul)': backdiluted_conc,
    'Backdilution sample final volume (ul)' : backdiluted_sample_total_volume_list 
})

# Create lists for source plate and well name for a Cherrypick from a water reservoir.
source_plate_name = 'Water'
source_well_name = 'A1'
source_plate_name_list = [source_plate_name] * len(filename_list)
source_well_name_list = [source_well_name] * len(filename_list)

# Create the cherrypick DataFrame
cherrypicking_df = pd.DataFrame({
    'SOURCE PLATE': source_plate_name_list,
    'SOURCE WELL NAME': source_well_name_list,
    'DESTINATION PLATE': backdilution_plate_id_list,
    'DESTINATION WELL NAME': well_id_list,
    'VOLUME (ul)': backdilution_volume_list
})

# Drop cherrypicks from the DataFrame where transfer volume = 0 to minimize tip waste
cherrypicking_zero_transfer_volume_row_indices = cherrypicking_df[(cherrypicking_df['VOLUME (ul)'] < 5.0)].index
cherrypicking_df.drop(cherrypicking_zero_transfer_volume_row_indices, inplace=True)

# Create a DataFrame from elution plates to get non-backdiluted well contents completely transferred.
low_conc_metadata_df = metadata_df[(metadata_df['Backdilution volume needed for normalization (ul)'] < 5.0) + (metadata_df['Backdilution sample final volume (ul)'] < 40.0)]
source_plate_name_list = low_conc_metadata_df['RNA Elution Plate #'].tolist()
source_well_name_list = low_conc_metadata_df['Well ID'].tolist()
destination_plate_name_list = low_conc_metadata_df['Backdilution Plate #'].tolist()
volume_list = [0]*len(source_well_name_list)

low_conc_cherrypicking_df = pd.DataFrame({
    'SOURCE PLATE': source_plate_name_list,
    'SOURCE WELL NAME': source_well_name_list,
    'DESTINATION PLATE': destination_plate_name_list,
    'DESTINATION WELL NAME': source_well_name_list,
    'VOLUME (ul)': volume_list
})

# Modify all elution volume and backdilution volume values to reflect completely transferred elution/backdilution wells.
elution_volumes = [elution_volume_1, elution_volume_2, elution_volume_3, elution_volume_4]
plate_names = ['Elution plate[001]','Elution plate[002]','Elution plate[003]','Elution plate[004]']
for i, elution_volume in enumerate(elution_volumes, start=1):
    condition = (source_plate_count >= i)
    if condition:
        if (rna_transfer_volume) < 40:
            extra_cherrypick_volume = 40 - rna_transfer_volume
            remaining_sample_volume = elution_volume - 40
            backdilution_sample_volume = 40
        if (rna_transfer_volume) >= 40:
            extra_cherrypick_volume = 0
            remaining_sample_volume = elution_volume - rna_transfer_volume
            backdilution_sample_volume = rna_transfer_volume

        plate_name = plate_names[i-1]
        low_conc_cherrypicking_df['VOLUME (ul)'] = low_conc_cherrypicking_df.apply(
            lambda row: row['VOLUME (ul)'] + extra_cherrypick_volume if row['SOURCE PLATE'] == plate_name else row['VOLUME (ul)'], axis=1
        )
        metadata_df['Elution sample remaining volume (ul)'] = metadata_df.apply(
            lambda row: remaining_sample_volume if (row['Backdilution volume needed for normalization (ul)'] < 5.0) and (row['RNA Elution Plate #'] == plate_name) else row['Elution sample remaining volume (ul)'], axis=1
        )
        metadata_df['Backdilution sample final volume (ul)'] = metadata_df.apply(
            lambda row: backdilution_sample_volume if (row['Backdilution volume needed for normalization (ul)'] < 5.0 or row['Backdilution sample final volume (ul)'] < 40) and (row['RNA Elution Plate #'] == plate_name) else row['Backdilution sample final volume (ul)'], axis=1
        )

low_conc_cherrypicking_zero_volume_row_indices = low_conc_cherrypicking_df[(low_conc_cherrypicking_df['VOLUME (ul)'] < 5.0)].index
low_conc_cherrypicking_df.drop(low_conc_cherrypicking_zero_volume_row_indices, inplace=True)

# Combine all cherrypicking dataframes.
combined_cherrypicking_df = pd.concat([cherrypicking_df, low_conc_cherrypicking_df], ignore_index=True)

# Format the current timestamp for file naming
current_time = datetime.now()
reformatted_datetime_string = current_time.strftime("%Y-%m-%d %H-%M-%S")

# Define file names
water_working_cherrypick_csv_filename = "Fluent_backdilution_cherrypick.csv" # This is what the Fluent uses to generate a .GWL worklist.
low_conc_working_cherrypick_csv_filename = "Low_Yield_Samples_Fluent_backdilution_cherrypick.csv" # This is what the Fluent uses to generate a .GWL worklist.

metadata_csv_filename = f"{reformatted_datetime_string}_Fluent backdilution_metadata.csv"
backup_cherrypick_csv_filename = f"{reformatted_datetime_string}_Fluent backdilution_cherrypick.csv"

# Define file paths
local_working_cherrypick_file_path = os.path.join(local_working_directory, water_working_cherrypick_csv_filename) # This is the local directory that contains temporary .CSV and .GWL files, referenced by FluentControl, overwritten during each scriptrun.
low_conc_working_cherrypick_file_path = os.path.join(local_working_directory, low_conc_working_cherrypick_csv_filename) # This is the local directory that contains temporary .CSV and .GWL files, referenced by Fluen

local_metadata_file_path = os.path.join(local_storage_directory, metadata_csv_filename)
gdrive_metadata_file_path = os.path.join(gdrive_metadata_storage_directory, metadata_csv_filename)
local_backup_cherrypick_file_path = os.path.join(local_storage_directory, backup_cherrypick_csv_filename)
gdrive_cherrypick_file_path = os.path.join(gdrive_cherrypick_storage_directory, backup_cherrypick_csv_filename)

# Export DataFrames to CSV
cherrypicking_df.to_csv(local_working_cherrypick_file_path, index=False) # This exports the CSV that FluentControl references for .GWL file generation.
low_conc_cherrypicking_df.to_csv(low_conc_working_cherrypick_file_path, index=False) # This exports the CSV that FluentControl references for .GWL file generation.

metadata_df.to_csv(local_metadata_file_path, index=False) # Export a local copy of metadata.
metadata_df.to_csv(gdrive_metadata_file_path, index=False) # Export a copy of metadata to RnD Transfer.
combined_cherrypicking_df.to_csv(local_backup_cherrypick_file_path, index=False) # Export a local copy of cherrypick.
combined_cherrypicking_df.to_csv(gdrive_cherrypick_file_path, index=False) # Export a copy of cherrypick to RnD Transfer.

cherrypicking_df.to_csv('G:/.shortcut-targets-by-id/1V3zHAt-KtgEHOLBdDqNfpfAGsRY6myLO/Automation/Tecan Fluent resources/Cherrypicks/Cherrypick optimizer/RNAP optimizer/rnap_nonoptimized_cp.csv', index=False) # Export a copy of cherrypick to the optimizer folder.