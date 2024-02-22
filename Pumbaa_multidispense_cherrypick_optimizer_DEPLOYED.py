import csv
import math
import pandas as pd

# Use FluentControl GetFile/Export Variables commands to obtain cherrypick filepath as a string, then pass string to reader for processing. 
exported_variables_file_path = "G:/.shortcut-targets-by-id/1V3zHAt-KtgEHOLBdDqNfpfAGsRY6myLO/Automation/Tecan Fluent resources/Cherrypicks/Cherrypick optimizer/pumbaa_exported_variables_file_path.csv"
filepath_df = pd.read_csv(exported_variables_file_path ,header=None)
cherrypick_filepath_string = str(filepath_df.iloc[1,0])
#cherrypick_filepath_string = "G:/.shortcut-targets-by-id/1V3zHAt-KtgEHOLBdDqNfpfAGsRY6myLO/Automation/Tecan Fluent resources/Cherrypicks/GetFile folder/Exp256_ nif Gene Screen S0085 - S0100 (Campaign 3) - (Left Side) Cherrypick Script.csv"

# Pass string to df via reader, then convert to dictionary. 
df = pd.read_csv(cherrypick_filepath_string, skiprows=0, header=0)
dfDict = df.to_dict('records')

# The following block creates a list of dictionaries, where each dictionary reps a unique Source Plate:Source Well combo, based on the imported df above.
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

# Construct the worklist (.gwl) file from scratch via string concatenation, using the new dictionary containing consolidated transfer keys.
tipmask_indices = ['1','2','4','8','16','32','64','128']
worklist_string = ''
aspirate_counter = 0
for each in range(0,len(transfer_info_consolidated)):
    
    if aspirate_counter == 8:
        aspirate_counter = 0
        
    tipmask = tipmask_indices[aspirate_counter]
    source_plate_id = transfer_info_consolidated[each]['Source Plate']
    source_well_id = transfer_info_consolidated[each]['Source Well']
    aspirate_volume = str(transfer_info_consolidated[each]['Total Volume'] + 0.05*transfer_info_consolidated[each]['Total Volume'])
    
    aspirate_string = 'A;'+ source_plate_id + ';;;' + source_well_id + ';;' + aspirate_volume + ';;;' + tipmask + ';\n'
    worklist_string += aspirate_string  
    
    for well in range(0,len(transfer_info_consolidated[each]['Destination Wells'])):
        dest_well_id = transfer_info_consolidated[each]['Destination Wells'][well]
        dest_plate_id = transfer_info_consolidated[each]['Destination Plates'][well]
        dispense_volume = str(transfer_info_consolidated[each]['Volumes'][well])
        
        dispense_string = 'D;'+ dest_plate_id + ';;;' + dest_well_id + ';;' + dispense_volume + ';;;' + tipmask + ';\n'
        
        if well == len(transfer_info_consolidated[each]['Destination Wells'])-1:
            dispense_string += 'W;\n'
            
        worklist_string += dispense_string 
    
    aspirate_counter += 1

# Finally, export the optimized multidispense worklist with filename = pumbaa_optimized_cherrypick.gwl
file_path = "G:/.shortcut-targets-by-id/1V3zHAt-KtgEHOLBdDqNfpfAGsRY6myLO/Automation/Tecan Fluent resources/Cherrypicks/Cherrypick optimizer/pumbaa_optimized_cherrypick.gwl"
with open(file_path, 'w') as file:
    file.write(worklist_string)