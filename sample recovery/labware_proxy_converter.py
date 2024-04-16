import pandas as pd

# Take user input for destinationLabwareProxy from the Fluent's ExportFile command.
export_filepath = "C:/Users/Tecan/Desktop/Tecan Fluent780 desktop files/sample_recovery/destinationLabwareProxy.csv"
user_inputs = pd.read_csv(export_filepath, header=None)
destinationLabwareProxy = user_inputs.iloc[1,0]

# Logic tree for proxy-to-backend labware definition name conversion.
if destinationLabwareProxy == "250uL PCR plate":
    destinationLabware = "96w NEST PCR Clear 250ul PP Clear conical bottom 402601"

if destinationLabwareProxy == "350uL flat-bottom plate":
    destinationLabware = "96w Corning Clear 360ul PS Clear flat bottom 9017"

if destinationLabwareProxy == "450uL v-bottom plate":
    destinationLabware = "96w Axygen Clear 450ul PP Clear V bottom P96450VCS"

if destinationLabwareProxy == "1mL round-bottom plate":
    destinationLabware = "96w Nunc Clear 1.3ml PP Clear, white round bottom 260252"

if destinationLabwareProxy == "2mL round-bottom plate":
    destinationLabware = "96w Nunc Clear 2ml PP Clear, white round bottom 278743"

if destinationLabwareProxy == "86mL diamond-bottom reservoir":
    destinationLabware = "96w Axygen Reservoir Clear 86ml PP Clear diamond bottom RESSW96LPSI"

if destinationLabwareProxy == "300mL flat-bottom reservoir":
    destinationLabware = "96w Nalgene Reservoir Clear 345ml PP Clear flat bottom 12001301"

# Export variable to a CSV via dataframe to CSV conversion. Variable will be imported by Fluent's ImportFile command.
destinationLabware_df = pd.DataFrame({
    'destinationLabware' : [destinationLabware]
})

import_filepath = "C:/Users/Tecan/Desktop/Tecan Fluent780 desktop files/sample_recovery/"
destinationLabware_df.to_csv(import_filepath +"destinationLabware.csv", index=False)