# This is the cherrypick optimizer script for RNAP.

import math
import pandas as pd

# Import the most recently generated, temporary copy of non-optimized cherrypick CSV from the RNAP script. This will be used for optimization. 
cherrypick_filepath_string = "G:/.shortcut-targets-by-id/1V3zHAt-KtgEHOLBdDqNfpfAGsRY6myLO/Automation/Tecan Fluent resources/Cherrypicks/Cherrypick optimizer/RNAP optimizer/rnap_nonoptimized_cp.csv"

# Pass string to df via reader, then convert to dictionary. 
df = pd.read_csv(cherrypick_filepath_string, skiprows=0, header=0)
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
gdrive_file_path = "G:/.shortcut-targets-by-id/1V3zHAt-KtgEHOLBdDqNfpfAGsRY6myLO/Automation/Tecan Fluent resources/Cherrypicks/Cherrypick optimizer/RNAP optimizer/rnap_optimized_cp.gwl"
with open(gdrive_file_path, 'w') as file:
    file.write(worklist_string)
