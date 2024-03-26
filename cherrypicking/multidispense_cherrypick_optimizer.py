# To run in terminal: cd Documents/GitHub/automation-Tecan-Fluent/cherrypicking/
# python multidispense_cherrypick_optimizer.py

# first things first, import things
import pandas as pd
import math
from datetime import datetime

# Use FluentControl GetFile/Export Variables commands to obtain cherrypick filepath as a string, then pass string to reader for processing. 
exported_variables_directory = "C:/Users/Tecan/Desktop/Tecan Fluent desktop files/cherrypicks/"
#exported_variables_directory = "C:/Users/Max/Desktop/Fluent cherrypick optimization testing/"
filepath_df = pd.read_csv(exported_variables_directory + 'getFile_exported_filepath.csv', header=None)
cherrypick_filepath_string = str(filepath_df.iloc[1,0])

# Get the tip capacity from FluentControl, dependent on user-selected tip type.
user_inputs = pd.read_csv(exported_variables_directory + 'tipCapacity.csv', header=None)
#tip_type = float(user_inputs.iloc[1,0])
#tip_capacity = 0.9*tip_type
tip_capacity = float(user_inputs.iloc[1,0])

# datetime utilization block here
current_time = datetime.now()
reformatted_datetime_string = current_time.strftime("%Y-%m-%d %H-%M-%S")
datetime_df = pd.DataFrame({
    'dateTime' : [reformatted_datetime_string]
})
datetime_df.to_csv(exported_variables_directory + "dateTime.csv", index=False)

# Pass string to df via reader, then convert to dictionary. 
df = pd.read_csv(cherrypick_filepath_string, skiprows=0, header=0)
dfDict = df.to_dict('records')

# Create a list of dictionaries, where each dictionary reps a unique SOURCE PLATE:SOURCE WELL NAME combo, based on the imported df above.
# Output transfer_info_consolidated list is used as a reference to iterate through transfers in GWL string construction block.
transfer_info_consolidated = []
for transfer in dfDict:
    # Get the unique identifier for each transfer
    transfer_key = (transfer['Source Plate'], transfer['Source Well'])

    # Check if the transfer_key already exists in transfer_info_consolidated
    transfer_exists = False
    for consolidated_transfer in transfer_info_consolidated:
        if (consolidated_transfer['Source Plate'], consolidated_transfer['Source Well']) == transfer_key:
            # If transfer already exists in transfer_info_consolidated, update the lists
            consolidated_transfer['Destination Wells'].append(transfer['Destination Well'])
            consolidated_transfer['Volumes'].append(float(transfer['Volume']))
            consolidated_transfer['Destination Plates'].append(transfer['Destination Plate'])
            consolidated_transfer['Total Volume'] += float(transfer['Volume'])
            consolidated_transfer['Dispense Count'] = len(consolidated_transfer['Destination Wells'])
            transfer_exists = True
            break

    if not transfer_exists:
        # If transfer does not exist in transfer_info_consolidated, create a new dictionary
        dest_well_list = [transfer['Destination Well']]
        volumes_list = [float(transfer['Volume'])]
        dest_plate_list = [transfer['Destination Plate']]
        total_volume = float(transfer['Volume'])
        dispense_count = 1
        transfer_info_consolidated.append({
            'Source Plate': transfer['Source Plate'],
            'Source Well': transfer['Source Well'],
            'Destination Plates': dest_plate_list,
            'Destination Wells': dest_well_list,
            'Volumes': volumes_list,
            'Total Volume': total_volume,
            'Dispense Count': dispense_count
        })

# Worklist generation magic starts here. The above transfer_info_consolidated dictionary will be used for string concatenation, for export as a custom GWL file.
tipmask_indices = ['1','2','4','8','16','32','64','128']
worklist_string = ''
aspirate_counter = 0

for transfer in transfer_info_consolidated:
    total_volume = transfer['Total Volume']
    source_plate = transfer['Source Plate']
    source_well = transfer['Source Well']
    num_aspirates = math.ceil(total_volume / tip_capacity)
    
    for aspirate_num in range(num_aspirates):
        if aspirate_counter >= len(tipmask_indices):
            aspirate_counter = 0
        tipmask = tipmask_indices[aspirate_counter]
        #tipmask=""
        
        if aspirate_num < num_aspirates - 1:
            aspirate_volume = tip_capacity
        else:
            aspirate_volume = total_volume - (tip_capacity * (num_aspirates - 1))

        worklist_string += f'A;{source_plate};;;{source_well};;{aspirate_volume:.2f};;;{tipmask};\n'
                
        remaining_volume = aspirate_volume
        for dispense_idx, dispense_volume in enumerate(transfer['Volumes']):
            if remaining_volume <= 0:
                break  # No volume left to dispense in this cycle
            
            if dispense_volume > 0:
                dispensed_volume = min(dispense_volume, remaining_volume)
                transfer['Volumes'][dispense_idx] -= dispensed_volume
                remaining_volume -= dispensed_volume
                
                dest_plate = transfer['Destination Plates'][dispense_idx]
                dest_well = transfer['Destination Wells'][dispense_idx]
                    
                worklist_string += f'D;{dest_plate};;;{dest_well};;{dispensed_volume:.2f};;;{tipmask};\n'
        """
        if tip_capacity == 900.0:
            disposal_volume = aspirate_volume * 0.05 # This is the value to change depending upon LC excess volume formula.

        if tip_capacity == 180.0:
            disposal_volume = aspirate_volume * 0.05 # This is the value to change depending upon LC excess volume formula.

        if tip_capacity == 45.0:
            disposal_volume = aspirate_volume * 0.05 # This is the value to change depending upon LC excess volume formula.

        if tip_capacity == 9.5:
            disposal_volume = aspirate_volume * 0.05 # This is the value to change depending upon LC excess volume formula.
        """
        disposal_volume = 0.05*tip_capacity
        empty_tips_string = f'D;{source_plate};;;{source_well};;{disposal_volume};;;{tipmask};\n'
        worklist_string += empty_tips_string + 'W;\n'
        aspirate_counter += 1

# Export the worklist to a textfile with .GWL file extension.
filepath = "C:/Users/Tecan/Desktop/Tecan Fluent desktop files/cherrypicks/log/" + reformatted_datetime_string  + "_multidispense_optimized_cherrypick.gwl"
#filepath = "C:/Users/Max/Desktop/Fluent cherrypick optimization testing/" + reformatted_datetime_string + "_optimized_cp.gwl"
with open(filepath, 'w') as file:
    file.write(worklist_string)