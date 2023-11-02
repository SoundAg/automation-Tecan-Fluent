# The following code was refactored from RNAP_python_script_v3_LOCAL.py using generative AI, with an emphasis on simplification, reorganization, and readability. 
# To run: cd C:/Users/Max/Desktop/RNAP backdilution testing/ then python RNAP_python_script_v4_LOCAL.py

import os
import pandas as pd
import numpy as np
from datetime import datetime

# Step 1: Import FluentControl variables contained in a CSV.
# Define the CSV file path.
filepath = "C:/Users/Max/Desktop/RNAP backdilution testing/store/fluent_control_var_exports.csv"

# Load the CSV file into a DataFrame.
df = pd.read_csv(filepath, header=None)
source_plate_count, norm_conc_1, norm_conc_2, norm_conc_3, norm_conc_4, elution_volume_1, elution_volume_2, elution_volume_3, elution_volume_4 = df.iloc[1, :].astype(float)

# Step 2: Make a dictionary of filepaths and their modification times.
folder_path = "C:/Users/Max/Desktop/RNAP backdilution testing/measurement_files/"
file_dates_modified = {os.path.join(folder_path, filename): os.path.getmtime(os.path.join(folder_path, filename)) for filename in os.listdir(folder_path) if filename.endswith(".csv")}

# Step 3: Sort filepaths by modification time and select the most recent (based on source_plate_count value imported from FluentControl).
files_sorted_by_modification_time = dict(sorted(file_dates_modified.items(), key=lambda x: x[1], reverse=True))
recent_run_filepaths = list(files_sorted_by_modification_time)[int(source_plate_count)-1::-1]

# Step 4: Process CSV files.
plate_96_rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
plate_96_columns = [str(num) for num in range(1, 13)]
plate_96_wells = [row + column for column in plate_96_columns for row in plate_96_rows]

#standards_xylose_concentrations = [0.0, 20.0, 40.0, 60.0, 80.0, 100.0, 150.0, 200.0]
standards_xylose_concentrations = [200.0, 150.0, 100.0, 80.0, 60.0, 40.0, 20.0, 0.0]
elution_plate_id_list, backdilution_plate_id_list, filename_list, well_id_list, od_data_list = [], [], [], [], []

for loop_count, csv_filepath in enumerate(recent_run_filepaths, start=1):
    elution_plate_id = f'Elution plate[00{loop_count}]'
    backdilution_plate_id = f'Backdilution plate[00{loop_count}]'
    
    df = pd.read_csv(csv_filepath, header=None)
    extracted_data = df.iloc[1:9, 1:13].values

    standards_od_data = list(df.iloc[1:9, 12].astype(float))
    slope, y_intercept = np.polyfit(standards_od_data, standards_xylose_concentrations, 1)

    transposed_data = extracted_data.T
    od_data_list.extend([float(val) for sublist in transposed_data for val in sublist])

    normalization_concentration = locals()[f'norm_conc_{loop_count}']
    elution_volume = locals()[f'elution_volume_{loop_count}']

    rna_transfer_volume = elution_volume / 2
    calculated_rna_conc_list = [(val * slope) + y_intercept for val in od_data_list]

    backdilution_volume_list = [round(((rna_transfer_volume * (conc / normalization_concentration)) - rna_transfer_volume), 1) if (conc / normalization_concentration) > 1.0 else 0.0 for conc in calculated_rna_conc_list]

    new_conc_list = [round((conc * rna_transfer_volume) / (rna_transfer_volume + backdilution_volume), 2) for conc, backdilution_volume in zip(calculated_rna_conc_list, backdilution_volume_list)]

    num_values = 96
    elution_plate_id_list.extend([elution_plate_id] * num_values)
    backdilution_plate_id_list.extend([backdilution_plate_id] * num_values)

    filename_list.extend([os.path.basename(csv_filepath)] * num_values)
    well_id_list.extend(plate_96_wells[:num_values])

metadata_df = pd.DataFrame({
    'Measurement file name': filename_list,
    'Well ID': well_id_list,
    'RNA Elution Plate #': elution_plate_id_list,
    'OD660': od_data_list,
    'Elution Plate RNA conc (ng/ul)': calculated_rna_conc_list,
    'Backdilution volume needed for normalization (ul)': backdilution_volume_list,
    'Backdilution Plate RNA conc (ng/ul)': new_conc_list,
    'Backdilution Plate #': backdilution_plate_id_list
})

# Create lists for source plate and well names
source_plate_name = 'Water'
source_well_name = 'A1'
source_plate_name_list = [source_plate_name] * len(backdilution_plate_id_list)
source_well_name_list = [source_well_name] * len(backdilution_plate_id_list)

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
working_directory = "C:/Users/Max/Desktop/RNAP backdilution testing/working directory/"
storage_directory = "C:/Users/Max/Desktop/RNAP backdilution testing/automated backdilution cherrypick logs/"

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
