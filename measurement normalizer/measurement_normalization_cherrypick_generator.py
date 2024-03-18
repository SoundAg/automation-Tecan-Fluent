# Commandline scriptrun: cd Users/Tecan/Documnets/GitHub/automation-Tecan-Fluent/measurement_normalization_cherrypick_generator.py

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
measurement_filepath = "G:/.shortcut-targets-by-id/1SA9d7OhoYdnH2QPxGxtxoE_0ZB5ZlyCP/RnD Transfer/Byonoy/measurement normalizer/norm_tester.csv"
df = pd.read_csv(measurement_filepath, header=None)
columnwise_od_values = list(pd.melt(df.iloc[1:9, 1:13], var_name = "column", value_name = "od")["od"])

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
#filepath = "G:/.shortcut-targets-by-id/1SA9d7OhoYdnH2QPxGxtxoE_0ZB5ZlyCP/RnD Transfer/Byonoy/measurement normalizer/errorToggle.csv"
local_filepath = "C:/Users/Tecan/Desktop/Tecan Fluent780 desktop files/measurement_and_normalization/"
warning_df.to_csv(local_filepath+"errorToggle.csv", index=False)

# Clean up the metadata to reflect reality (no negative volumes).
metadata_df.loc[metadata_df['sample volume for backdilution'] > target_vol, 'sample volume for backdilution'] = 0
metadata_df.loc[metadata_df['remaining sample volume'] < 0, 'remaining sample volume'] = starting_sample_vol
metadata_df.loc[metadata_df['diluent volume for backdilution'] < 0, 'diluent volume for backdilution'] = 0
metadata_df.loc[metadata_df['sample volume for backdilution'] <= 0, 'diluted sample volume'] = 0

# Build the cherrypick using only valid, nonzero volume values.
cleaned_metadata_df = metadata_df.drop(metadata_neg_value_error_df.index)
cherrypick_df_diluent = pd.DataFrame({
    'SOURCE PLATE': ["Diluent" for val in range(0,len(cleaned_metadata_df))],
    'SOURCE WELL NAME': ["A1" for val in range(0,len(cleaned_metadata_df))],
    'DESTINATION PLATE': ["Dilution plate" for val in range(0,len(cleaned_metadata_df))],
    'DESTINATION WELL NAME': cleaned_metadata_df["well id"],
    'VOLUME (ul)': cleaned_metadata_df['diluent volume for backdilution']
})
cherrypick_df_samples = pd.DataFrame({
    'SOURCE PLATE': ["Sample plate" for val in range(0,len(cleaned_metadata_df))],
    'SOURCE WELL NAME': cleaned_metadata_df["well id"],
    'DESTINATION PLATE': ["Dilution plate" for val in range(0,len(cleaned_metadata_df))],
    'DESTINATION WELL NAME': cleaned_metadata_df["well id"],
    'VOLUME (ul)': cleaned_metadata_df['sample volume for backdilution']
})
combined_cherrypick_df = pd.concat([cherrypick_df_diluent, cherrypick_df_samples], ignore_index=True)

# Setup the finalized cherrypick df for export.
current_time = datetime.now()
reformatted_datetime_string = current_time.strftime("%Y-%m-%d %H-%M-%S")
datetime_df = pd.DataFrame({
    'dateTime' : [reformatted_datetime_string]
})
datetime_df.to_csv(local_filepath+"dateTime.csv", index=False)

temp_cherrypick_csv_filename = "normalization_backdilution_cherrypick.csv" # This is what the Fluent uses to generate a .GWL worklist.
backup_cherrypick_csv_filename = f"{reformatted_datetime_string}_Fluent backdilution_cherrypick.csv"
metadata_csv_filename = f"{reformatted_datetime_string}_Fluent backdilution_metadata.csv"

gdrive_directory_filepath = "G:/.shortcut-targets-by-id/1SA9d7OhoYdnH2QPxGxtxoE_0ZB5ZlyCP/RnD Transfer/Byonoy/measurement normalizer/"
temp_cherrypick_filepath = os.path.join(local_filepath, temp_cherrypick_csv_filename)
backup_cherrypick_filepath = os.path.join(gdrive_directory_filepath, backup_cherrypick_csv_filename)
metadata_filepath = os.path.join(gdrive_directory_filepath, metadata_csv_filename)

metadata_df.to_csv(metadata_filepath, index=False)
combined_cherrypick_df.to_csv(backup_cherrypick_filepath, index=False)
combined_cherrypick_df.to_csv(temp_cherrypick_filepath, index=False)

#Cherrypick optimization time.
# Pass string to df via reader, then convert to dictionary. 
df = pd.read_csv(backup_cherrypick_filepath, skiprows=0, header=0)
dfDict = df.to_dict('records')

# The following block creates a list of dictionaries, where each dictionary reps a unique SOURCE PLATE:SOURCE WELL NAME combo, based on the imported df above.
# Output transfer_info_consolidated list is used as a reference to iterate through transfers in GWL string construction block.
transfer_info_consolidated = []
for transfer in dfDict:
    # Get the unique identifier for each transfer
    transfer_key = (transfer['SOURCE PLATE'], transfer['SOURCE WELL NAME'])

    # Check if the transfer_key already exists in transfer_info_consolidated
    transfer_exists = False
    for consolidated_transfer in transfer_info_consolidated:
        if (consolidated_transfer['SOURCE PLATE'], consolidated_transfer['SOURCE WELL NAME']) == transfer_key:
            # If transfer already exists in transfer_info_consolidated, update the lists
            consolidated_transfer['DESTINATION WELLS'].append(transfer['DESTINATION WELL NAME'])
            consolidated_transfer['VOLUMES'].append(float(transfer['VOLUME (ul)']))
            consolidated_transfer['DESTINATION PLATES'].append(transfer['DESTINATION PLATE'])
            consolidated_transfer['TOTAL VOLUME'] += float(transfer['VOLUME (ul)'])
            consolidated_transfer['DISPENSE COUNT'] = len(consolidated_transfer['DESTINATION WELLS'])
            transfer_exists = True
            break

    if not transfer_exists:
        # If transfer does not exist in transfer_info_consolidated, create a new dictionary
        dest_well_list = [transfer['DESTINATION WELL NAME']]
        volumes_list = [float(transfer['VOLUME (ul)'])]
        dest_plate_list = [transfer['DESTINATION PLATE']]
        total_volume = float(transfer['VOLUME (ul)'])
        dispense_count = 1
        transfer_info_consolidated.append({
            'SOURCE PLATE': transfer['SOURCE PLATE'],
            'SOURCE WELL NAME': transfer['SOURCE WELL NAME'],
            'DESTINATION PLATES': dest_plate_list,
            'DESTINATION WELLS': dest_well_list,
            'VOLUMES': volumes_list,
            'TOTAL VOLUME': total_volume,
            'DISPENSE COUNT': dispense_count
        })

# Worklist generation magic starts here. The above transfer_info_consolidated dictionary will be used for string concatenation, for export as a custom GWL file.
tip_capacity = 900.0
tipmask_indices = ['1','2','4','8','16','32','64','128']
worklist_string = ''
aspirate_counter = 0

for transfer in transfer_info_consolidated:
    total_volume = transfer['TOTAL VOLUME']
    source_plate = transfer['SOURCE PLATE']
    source_well = transfer['SOURCE WELL NAME']
    num_aspirates = math.ceil(total_volume / tip_capacity)
    
    for aspirate_num in range(num_aspirates):
        if aspirate_counter >= len(tipmask_indices):
            aspirate_counter = 0
        #tipmask = tipmask_indices[aspirate_counter]
        tipmask=""
        
        if aspirate_num < num_aspirates - 1:
            aspirate_volume = tip_capacity
        else:
            aspirate_volume = total_volume - (tip_capacity * (num_aspirates - 1))
        
        worklist_string += f'A;{source_plate};;;{source_well};;{aspirate_volume:.2f};;;{tipmask};\n'
        
        remaining_volume = aspirate_volume
        for dispense_idx, dispense_volume in enumerate(transfer['VOLUMES']):
            if remaining_volume <= 0:
                break  # No volume left to dispense in this cycle
            
            if dispense_volume > 0:
                dispensed_volume = min(dispense_volume, remaining_volume)
                transfer['VOLUMES'][dispense_idx] -= dispensed_volume
                remaining_volume -= dispensed_volume
                
                dest_plate = transfer['DESTINATION PLATES'][dispense_idx]
                dest_well = transfer['DESTINATION WELLS'][dispense_idx]
                worklist_string += f'D;{dest_plate};;;{dest_well};;{dispensed_volume:.2f};;;{tipmask};\n'
                
        worklist_string += 'W;\n'
        aspirate_counter += 1

# Finally, export the optimized multidispense worklist with filename = rnap_optimized_cp.csv
gwl_filepath = local_filepath + "optimized_cp.gwl"
with open(gwl_filepath, 'w') as file:
    file.write(worklist_string)