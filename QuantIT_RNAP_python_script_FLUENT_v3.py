# The following code was updated from the QuantIT_RNAP_python_script_LOCAL_v1
# To run: cd C:/Users/Tecan/Desktop/Tecan Fluent desktop files/RNAP data management
# python QuantIT_RNAP_python_script_FLUENT_v2.py

import os
import pandas as pd
import numpy as np
from datetime import datetime
from statistics import mean, median, mode

# Step 1: Import FluentControl variables contained in a CSV.
# Define the CSV file path.
filepath = "C:/Users/Tecan/Desktop/Tecan Fluent desktop files/RNAP data management/rnap_automated_backdilution_cherrypick_inputs.csv"

# Load the CSV file into a DataFrame.
df = pd.read_csv(filepath ,header=None)
source_plate_count, norm_conc_1, norm_conc_2, norm_conc_3, norm_conc_4, elution_volume_1, elution_volume_2, elution_volume_3, elution_volume_4 = df.iloc[1, :].astype(float)
source_plate_count = int(source_plate_count)

# Step 2: Make a dictionary of filepaths and their modification times.
folder_path = "G:/.shortcut-targets-by-id/1kOpNriLPL3kgZ-DM8TK4O3Bw06XKmk6M/Research/RnD Transfer/Spark/RNA QUANT MEASUREMENT FILES/"
file_dates_modified = {os.path.join(folder_path, filename): os.path.getmtime(os.path.join(folder_path, filename)) for filename in os.listdir(folder_path) if filename.endswith(".xlsx")}

# Step 3: Sort filepaths by modification time and select the most recent (based on source_plate_count value imported from FluentControl).
files_sorted_by_modification_time = dict(sorted(file_dates_modified.items(), key=lambda x: x[1], reverse=True))
recent_measurement_filepaths = list(files_sorted_by_modification_time)[:source_plate_count+1]
reordered_measurement_filepaths = recent_measurement_filepaths[::-1]
only_measurement_filepaths = reordered_measurement_filepaths[1:]
standards_filepath = reordered_measurement_filepaths[0]

# Step 4: Process Standards data from the Lambda rRNA standards assay plate.

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

lambda_standards_concentrations = [0.0, 5.0, 10.0, 20.0, 40.0, 60.0, 80.0, 100.0]
lambda_standards_concentrations_array = []
for each in range(0,len(lambda_standards_concentrations)):
    for n in range(0,12):
        lambda_standards_concentrations_array.append(lambda_standards_concentrations[each])
        
slope, y_intercept = np.polyfit(all_standards_rfu_values, lambda_standards_concentrations_array, 1)

# Step 5: Process Excel files.
plate_96_rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
plate_96_columns = [str(num) for num in range(1, 13)]
plate_96_wells = [row + column for column in plate_96_columns for row in plate_96_rows]

filename_list, well_id_list, elution_plate_id_list, backdilution_plate_id_list = [],[],[],[]
rfu_data_list_1, rfu_data_list_2, rfu_data_list_3, rfu_data_list_4 = [],[],[],[]
calculated_rna_conc_list_1, calculated_rna_conc_list_2, calculated_rna_conc_list_3, calculated_rna_conc_list_4 = [],[],[],[]
backdilution_volume_list_1, backdilution_volume_list_2, backdilution_volume_list_3, backdilution_volume_list_4 = [],[],[],[]
backdiluted_conc_1, backdiluted_conc_2, backdiluted_conc_3, backdiluted_conc_4 = [],[],[],[]

for loop_count, excel_filepath in enumerate(only_measurement_filepaths, start=1):
    elution_plate_id = f'Elution plate[00{loop_count}]'
    backdilution_plate_id = f'Backdilution plate[00{loop_count}]'
    normalization_concentration = locals()[f'norm_conc_{loop_count}']
    elution_volume = locals()[f'elution_volume_{loop_count}']
    rna_transfer_volume = elution_volume / 2
    
    df = pd.read_excel(excel_filepath)
    extracted_data = df.iloc[53:61, 1:13].values
    transposed_data = extracted_data.T

    if loop_count == 1:
        rfu_data_list_1 = [float(val) for sublist in transposed_data for val in sublist]
        calculated_rna_conc_list_1 = [((val * slope * 2) + y_intercept) for val in rfu_data_list_1]
        backdilution_volume_list_1 = [round(((rna_transfer_volume * conc / normalization_concentration) - rna_transfer_volume), 1) if conc > normalization_concentration else 0.0 for conc in calculated_rna_conc_list_1]
        for each in range(0,len(calculated_rna_conc_list_1)):
            backdiluted_conc = round((calculated_rna_conc_list_1[each] * rna_transfer_volume)/(rna_transfer_volume + backdilution_volume_list_1[each]), 2)
            backdiluted_conc_1.append(backdiluted_conc)
    if loop_count == 2: 
        rfu_data_list_2 = [float(val) for sublist in transposed_data for val in sublist]
        calculated_rna_conc_list_2 = [((val * slope * 2) + y_intercept) for val in rfu_data_list_2]
        backdilution_volume_list_2 = [round(((rna_transfer_volume * conc / normalization_concentration) - rna_transfer_volume), 1) if conc > normalization_concentration else 0.0 for conc in calculated_rna_conc_list_2]
        for each in range(0,len(calculated_rna_conc_list_2)):
            backdiluted_conc = round((calculated_rna_conc_list_2[each] * rna_transfer_volume)/(rna_transfer_volume + backdilution_volume_list_2[each]), 2)
            backdiluted_conc_2.append(backdiluted_conc)
    if loop_count == 3: 
        rfu_data_list_3 = [float(val) for sublist in transposed_data for val in sublist]
        calculated_rna_conc_list_3 = [((val * slope * 2) + y_intercept) for val in rfu_data_list_3]
        backdilution_volume_list_3 = [round(((rna_transfer_volume * conc / normalization_concentration) - rna_transfer_volume), 1) if conc > normalization_concentration else 0.0 for conc in calculated_rna_conc_list_3]
        for each in range(0,len(calculated_rna_conc_list_3)):
            backdiluted_conc = round((calculated_rna_conc_list_3[each] * rna_transfer_volume)/(rna_transfer_volume + backdilution_volume_list_3[each]), 2)
            backdiluted_conc_3.append(backdiluted_conc)   
    if loop_count == 4: 
        rfu_data_list_4 = [float(val) for sublist in transposed_data for val in sublist]
        calculated_rna_conc_list_4 = [((val * slope * 2) + y_intercept) for val in rfu_data_list_4]
        backdilution_volume_list_4 = [round(((rna_transfer_volume * conc / normalization_concentration) - rna_transfer_volume), 1) if conc > normalization_concentration else 0.0 for conc in calculated_rna_conc_list_4]
        for each in range(0,len(calculated_rna_conc_list_4)):
            backdiluted_conc = round((calculated_rna_conc_list_4[each] * rna_transfer_volume)/(rna_transfer_volume + backdilution_volume_list_4[each]), 2)
            backdiluted_conc_4.append(backdiluted_conc)
            
    num_values = 96
    filename_list.extend([os.path.basename(excel_filepath)] * num_values)
    well_id_list.extend(plate_96_wells[:num_values])
    elution_plate_id_list.extend([elution_plate_id] * num_values)
    backdilution_plate_id_list.extend([backdilution_plate_id] * num_values)
    
rfu_data_list = rfu_data_list_1 + rfu_data_list_2 + rfu_data_list_3 + rfu_data_list_4
calculated_rna_conc_list = calculated_rna_conc_list_1 + calculated_rna_conc_list_2 + calculated_rna_conc_list_3 + calculated_rna_conc_list_4
backdilution_volume_list = backdilution_volume_list_1 + backdilution_volume_list_2 + backdilution_volume_list_3 + backdilution_volume_list_4
backdiluted_conc = backdiluted_conc_1 + backdiluted_conc_2 + backdiluted_conc_3 + backdiluted_conc_4

metadata_df = pd.DataFrame({
    'Measurement file name': filename_list,
    'Well ID': well_id_list,
    'RNA Elution Plate #': elution_plate_id_list,
    'RFU': rfu_data_list,
    'Elution Plate RNA conc (ng/ul)': calculated_rna_conc_list,
    'Backdilution volume needed for normalization (ul)': backdilution_volume_list,
    'Backdilution Plate RNA conc (ng/ul)': backdiluted_conc,
    'Backdilution Plate #': backdilution_plate_id_list
})

# Create lists for source plate and well names
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

# Format the current timestamp for file naming
current_time = datetime.now()
reformatted_datetime_string = current_time.strftime("%Y-%m-%d %H-%M-%S")

# Define storage and working directories
working_directory = "C:/Users/Tecan/Desktop/Tecan Fluent desktop files/RNAP data management/working directory/"
storage_directory = "C:/Users/Tecan/Desktop/Tecan Fluent desktop files/RNAP data management/automated backdilution cherrypick logs/"

# Define file names
metadata_csv_filename = f"{reformatted_datetime_string}_Fluent backdilution_metadata.csv"
backup_cherrypick_csv_filename = f"{reformatted_datetime_string}_Fluent backdilution_cherrypick.csv"
working_cherrypick_csv_filename = "Fluent_backdilution_cherrypick.csv"

# Define file paths
metadata_file_path = os.path.join(storage_directory, metadata_csv_filename)
backup_cherrypick_file_path = os.path.join(storage_directory, backup_cherrypick_csv_filename)
working_cherrypick_file_path = os.path.join(working_directory, working_cherrypick_csv_filename)

# Export DataFrames to CSV
metadata_df.to_csv(metadata_file_path, index=False)
cherrypicking_df.to_csv(backup_cherrypick_file_path, index=False)
cherrypicking_df.to_csv(working_cherrypick_file_path, index=False)