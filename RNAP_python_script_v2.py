# Import necessary libraries.
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Step 1: Import FluentControl variables contained in a CSV

#ENTER FLUENT LOCAL DIRECTORY CONTAINING CSV EXPORT HERE
filepath = "C:/Users/Tecan/Desktop/Tecan Fluent desktop files/RNAP data management/rnap_automated_backdilution_cherrypick_inputs.csv"
df = pd.read_csv(filepath, skiprows=0, header=None)
source_plate_count = int(df.iloc[1,0])
norm_conc_1 = float(df.iloc[1,1])
norm_conc_2 = float(df.iloc[1,2])
norm_conc_3 = float(df.iloc[1,3])
norm_conc_4 = float(df.iloc[1,4])
elution_volume_1 = float(df.iloc[1,5])
elution_volume_2 = float(df.iloc[1,6])
elution_volume_3 = float(df.iloc[1,7])
elution_volume_4 = float(df.iloc[1,8])

# Step 2: Make a dictionary of all filepaths and their creation times from your directory of choice, as key:value pairs.

#ENTER FLUENT LOCAL DIRECTORY CONTAINING BYONOY MEASUREMENT FILES HERE
folder_path = "C:/Users/Tecan/Desktop/Tecan Fluent desktop files/RNAP data management/byonoy automated csv exports/"
file_creation_times = {}

for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    creation_time = os.path.getctime(file_path)
    file_creation_times.update({file_path : creation_time})

# Step 3: Sort all filepaths by creation date, then only pick the sourcePlateCount number of most recent items.
files_sorted_by_creation_time = dict(sorted(file_creation_times.items(), key=lambda x:x[1]))
recent_run_filepaths = list(files_sorted_by_creation_time.keys())[0:source_plate_count]

# Step 4: Grab data from each CSV file, in order, importing it into a dataframe.

# Create a columnwise list of wells in a 96-well plate.
plate_96_rows = ["A","B","C","D","E","F","G","H"]
plate_96_columns = [str(num) for num in range(1,13)]
plate_96_wells = []
for column in plate_96_columns:
    for row in plate_96_rows:
        well = row + column
        plate_96_wells.append(well)

# Initialize lists needed to build final dataframes for CSV export.
filename_list = []
elution_plate_id_list = []
backdilution_plate_id_list = []
well_id_list = []
od_data_list = []
calculated_rna_conc_list = []
backdilution_volume_list = []
new_conc_list = []

# Adjust these values as needed, listed in order from H1-H8
standards_xylose_concentrations = [0.0, 20.0, 40.0, 60.0, 80.0, 100.0, 150.0, 200.0]

loop_count = 1
for csv_file in recent_run_filepaths:
    elution_plate_id = f'Elution plate[00{loop_count}]'
    backdilution_plate_id = f'Backdilution plate[00{loop_count}]'
    
    # Import CSV to dataframe.
    df = pd.read_csv(csv_file, skiprows=0, header=None)
    
    # Grab only relevant data.
    extracted_data = df.iloc[1:9, 1:13].values
    
    # Pull Xylose Standards data from column 12.
    standards_od_data = list(df.iloc[1:9,12])
    standards_od_data_floats = []
    for each in range(0,len(standards_od_data)):
        standards_od_data_floats.append(float(standards_od_data[each]))
    
    # Use standards data from column 12 to calculate LOBF.
    x = np.array(standards_od_data_floats)
    y = np.array(standards_xylose_concentrations)
    slope, y_intercept = np.polyfit(x, y, 1)
    
    # Transpose all OD data to stack it column-wise: each column becomes a list. Total data = a list containing 12 lists.
    transposed_data = extracted_data.T
    
    # Flatten the array containing OD data and add it to a new running list: 12 lists are merged end-to-end. Total data = 1 longer list.
    flattened_data = transposed_data.flatten()
    od_data_list.extend(flattened_data)
    
    # Change elution volumes for subsequent backdil volume calc math, per plate.
    if loop_count == 1:
        normalization_concentration = norm_conc_1
        elution_volume = elution_volume_1
    elif loop_count == 2: 
        normalization_concentration = norm_conc_2
        elution_volume = elution_volume_2
    elif loop_count == 3:
        normalization_concentration = norm_conc_3 
        elution_volume = elution_volume_3
    elif loop_count == 4:
        normalization_concentration = norm_conc_4
        elution_volume = elution_volume_4
    rna_transfer_volume = elution_volume / 2 # This can be user-specified in the future
    
    # Use OD data and LOBF from standards data to calculate RNA concentrations.
    for each in range(0,len(flattened_data)):
        calculated_rna_conc = (float(flattened_data[each]) * slope) + y_intercept
        calculated_rna_conc_list.append(calculated_rna_conc)

        # Then use calculated RNA concentration data and norm_conc values to get backdilution volumes.
        backdilution_ratio = calculated_rna_conc_list[each] / normalization_concentration
        if backdilution_ratio < 1.0:
            backdilution_volume = 0.0
        elif backdilution_ratio >= 1.0:
            backdilution_volume = round(((rna_transfer_volume * backdilution_ratio) - rna_transfer_volume),1)

        backdilution_volume_list.append(backdilution_volume)
        
        # Record all new conc values in a list.
        new_concentration = round(((calculated_rna_conc_list[each] * rna_transfer_volume) / (rna_transfer_volume + backdilution_volume)),2)
        new_conc_list.append(new_concentration)
            
    # Add the plate IDs for each value in the data (96 values).
    num_values = transposed_data.size
    elution_plate_id_list.extend([elution_plate_id] * num_values)
    backdilution_plate_id_list.extend([backdilution_plate_id] * num_values)
    
    # Add the source CSV filename for each value in the data (96 values).
    # Change 76 to some other number as needed
    filename = recent_run_filepaths[loop_count-1][76:]
    filename_list.extend([filename] * num_values)
    #print(filename_list)
    
    # Add the well ID for each value in the CSV to the well_id_list.
    well_id_list.extend(plate_96_wells[:num_values])
    #print(well_id_list)

    loop_count += 1

# Create a combined CSV file containing all metadata for recordkeeping purposes.
metadata_df = pd.DataFrame({
    'Filename': filename_list,
    'Elution Plate ID' : elution_plate_id_list,
    'Well ID' : well_id_list,
    'OD660' : od_data_list,
    'RNA conc (ng/ul)' : calculated_rna_conc_list,
    'Backdilution volume (ul)' : backdilution_volume_list,
    'New concentration (ng/ul)' : new_conc_list,
    'Backdilution Plate ID' : backdilution_plate_id_list
})

# Create lists of proper length to fill in slots for source plates and source wells in the cherrypick df.

source_plate_name = 'Water'
source_well_name = 'A1'
source_plate_name_list = []
source_well_name_list = []
for each in range(0,len(backdilution_plate_id_list)):
    source_plate_name_list.append(source_plate_name)
    source_well_name_list.append(source_well_name)

cherrypicking_df = pd.DataFrame({
    'SOURCE PLATE' : source_plate_name_list,
    'SOURCE WELL NAME' : source_well_name_list,
    'DESTINATION PLATE' : backdilution_plate_id_list,
    'DESTINATION WELL NAME' : well_id_list,
    'VOLUME (ul)' : backdilution_volume_list
})

# Turn current timestamp into a string for file naming purposes.
current_time = datetime.now()
current_time_as_string = str(current_time)
reformatted_datetime_string = ""
for char in current_time_as_string[0:19]:
    if char == ':':
        new_char = '-'
        reformatted_datetime_string += new_char
    else:
        reformatted_datetime_string += char

# Now finally export the metadata & cherrypick dfs as CSVs into storage folders and working folders.
working_directory = "C:/Users/Tecan/Desktop/Tecan Fluent desktop files/RNAP data management/working directory/"
storage_directory = "C:/Users/Tecan/Desktop/Tecan Fluent desktop files/RNAP data management/automated backdilution cherrypick logs/"

metadata_csv_filename = reformatted_datetime_string + "_Fluent backdilution_metadata"           
output_file_path = storage_directory + metadata_csv_filename + ".csv"
metadata_df.to_csv(output_file_path, index=False)

backup_cherrypick_csv_filename = reformatted_datetime_string + "_Fluent backdilution_cherrypick"        
output_file_path = storage_directory + backup_cherrypick_csv_filename + ".csv"
cherrypicking_df.to_csv(output_file_path, index=False)

working_cherrypick_csv_filename = "Fluent_backdilution_cherrypick"           
output_file_path = working_directory + working_cherrypick_csv_filename + ".csv"
cherrypicking_df.to_csv(output_file_path, index=False)