# This script generates a heatmap from Byonoy measurement files, to be displayed to users at runtime.

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Read data from CSV
local_filepath = "C:/Users/Tecan/Desktop/Tecan Fluent780 desktop files/measurement_and_normalization/"
byonoy_measurement_filepath_export = local_filepath + "byonoy_measurement_filepath.csv"
measurement_filepath = str(pd.read_csv(byonoy_measurement_filepath_export, header=None).iloc[1,0])
df = pd.read_csv(measurement_filepath, header=None, skiprows=1, nrows=8, usecols=range(1, 13))

# Create heatmap
plt.figure(figsize=(12, 8))
sns.set_theme(font_scale=1.2)
ax = sns.heatmap(df, annot=True, fmt='.2f', cmap='Greens', cbar_kws={'label': 'Value'})

# Set custom y-axis labels
ax.set_yticklabels(list('ABCDEFGH'), rotation=0)

plt.title('Heatmap of Your Data')
plt.xlabel('Columns')
plt.ylabel('Rows')
plt.tight_layout()

# Save as image
current_time = datetime.now()
reformatted_datetime_string = current_time.strftime("%Y-%m-%d %H-%M-%S")
filename = reformatted_datetime_string + " heatmap.png" 
plt.savefig(local_filepath + "Heatmap local log/" + filename, dpi=300, bbox_inches='tight')
plt.savefig(local_filepath + "temp heatmap", dpi=300, bbox_inches='tight')
#plt.show()

# Save to Drive locations for public access
gdrive_filepath = "G:/.shortcut-targets-by-id/1SA9d7OhoYdnH2QPxGxtxoE_0ZB5ZlyCP/RnD Transfer/Byonoy/measurement normalizer/Heatmap log/"
plt.savefig(gdrive_filepath + filename, dpi=300, bbox_inches='tight')


