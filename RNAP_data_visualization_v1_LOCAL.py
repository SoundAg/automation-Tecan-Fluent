# This script generates data plots using QuantIT values from the RNAP workflow.

import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime

# Declare all filepaths to be used in the script.
exported_variables_file_path = "C:/Users/Max/Desktop/RNAP backdilution testing/fluent_control_var_exports.csv"
measurement_files_folder_path = "C:/Users/Max/Desktop/RNAP backdilution testing/measurement_files"
metadata_folder_path = "C:/Users/Max/Desktop/RNAP backdilution testing/automated backdilution cherrypick logs/"
plot_file_path = "C:/Users/Max/Desktop/RNAP backdilution testing/automated backdilution cherrypick logs/"

# Import data inputs from FluentControl
df = pd.read_csv(exported_variables_file_path ,header=None)
source_plate_count, norm_conc_1, norm_conc_2, norm_conc_3, norm_conc_4, elution_volume_1, elution_volume_2, elution_volume_3, elution_volume_4 = df.iloc[1, :].astype(float)
source_plate_count = int(source_plate_count)

# Get the most recent measurement and standards files
file_dates_modified = {os.path.join(measurement_files_folder_path, filename): os.path.getmtime(os.path.join(measurement_files_folder_path, filename)) for filename in os.listdir(measurement_files_folder_path) if filename.endswith(".xlsx")}

#Sort filepaths by modification time and select the most recent (based on source_plate_count value imported from FluentControl).
files_sorted_by_modification_time = dict(sorted(file_dates_modified.items(), key=lambda x: x[1], reverse=True))
recent_measurement_filepaths = list(files_sorted_by_modification_time)[:source_plate_count+1]
reordered_measurement_filepaths = recent_measurement_filepaths[::-1]
standards_filepath = reordered_measurement_filepaths[0]

# STANDARDS SCATTERPLOT GENERATION
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
        
x_axis_label = "Standards RFU data"
y_axis_label = "Standards Concentrations (ng/ul)"

standards_data = {
    x_axis_label : all_standards_rfu_values,
    y_axis_label : standards_concentrations_array
}

new_standards_df = pd.DataFrame(standards_data)

# Perform linear regression
slope, intercept, r_value, p_value, std_err = linregress(new_standards_df[x_axis_label], new_standards_df[y_axis_label])
r_squared = r_value**2

# Create a subplot
fig, ax = plt.subplots(figsize=(10,10))

# Scatterplot
ax.scatter(new_standards_df[x_axis_label], new_standards_df[y_axis_label], label='Standards measurements')

# Line of best fit
ax.plot(new_standards_df[x_axis_label], slope * new_standards_df[x_axis_label] + intercept, color='red', label='Line of Best Fit')

# R-squared text
ax.text(0.9, 0.1, f'R-squared: {r_squared:.2f}', fontsize=12, color='red', ha='right', va='bottom', transform=ax.transAxes)

# Labels and title
ax.set_xlabel(x_axis_label, labelpad=20, fontsize=12)
ax.set_ylabel(y_axis_label, labelpad=20, fontsize=12)
ax.set_title("Quant-iT standards curve", fontsize=16, pad=10)

# Set y-axis ticks and labels
yticks = list(range(0, 121, 5))
ax.set_yticks(yticks)

y_tick_labels = ax.get_yticklabels()
for i, label in enumerate(y_tick_labels):
    if i % 2 != 0:  # Check if the index is odd
        label.set_visible(False)

# Save the subplot to a variable
standards_plot = plt.gcf()

# ELUTED RNA CONCENTRATION BOXPLOT GENERATION
file_dates_modified = {os.path.join(metadata_folder_path, filename): os.path.getmtime(os.path.join(metadata_folder_path, filename)) for filename in os.listdir(metadata_folder_path) if filename.endswith(".csv")}
files_sorted_by_modification_time = dict(sorted(file_dates_modified.items(), key=lambda x: x[1], reverse=True))
recent_metadata_filepath = list(files_sorted_by_modification_time)[0]

metadata_df = pd.read_csv(recent_metadata_filepath)

# Create a boxplot with points
metadata_x_axis = "RNA Elution Plate #"
rna_conc_y_axis = "Eluted RNA conc (ng/ul)"

fig_size_x_dimension = 2.5*source_plate_count
fig, ax = plt.subplots(figsize=(fig_size_x_dimension, 10))  # Set a larger height by adjusting the second value (height) in figsize
sns.boxplot(x=metadata_x_axis, y=rna_conc_y_axis, data=metadata_df, color='grey')
sns.stripplot(x=metadata_x_axis, y=rna_conc_y_axis, data=metadata_df, color='black', size=8, jitter=True)

plt.axhline(y=norm_conc_1, color='red', linestyle='--', linewidth=2, xmin=0,xmax=0.25, label='Backdilution normalization target')
ax.text(0, norm_conc_1, f'{norm_conc_1} ng/ul', color='black', backgroundcolor='white', ha='center', va='center', bbox=dict(facecolor='white', edgecolor='white', boxstyle='round,pad=0.5'))
if source_plate_count > 1:
    plt.axhline(y=norm_conc_2, color='red', linestyle='--', xmin=0.25,xmax=0.50)
    ax.text(1, norm_conc_2, f'{norm_conc_2} ng/ul', color='black', backgroundcolor='white', ha='center', va='center', bbox=dict(facecolor='white', edgecolor='white', boxstyle='round,pad=0.5'))
if source_plate_count > 2:
    plt.axhline(y=norm_conc_3, color='red', linestyle='--', xmin=0.50,xmax=0.75)
    ax.text(2, norm_conc_3, f'{norm_conc_3} ng/ul', color='black', backgroundcolor='white', ha='center', va='center', bbox=dict(facecolor='white', edgecolor='white', boxstyle='round,pad=0.5'))
if source_plate_count > 3:
    plt.axhline(y=norm_conc_4, color='red', linestyle='--', xmin=0.75,xmax=1.0)
    ax.text(3, norm_conc_4, f'{norm_conc_4} ng/ul', color='black', backgroundcolor='white', ha='center', va='center', bbox=dict(facecolor='white', edgecolor='white', boxstyle='round,pad=0.5'))

# Set labels and legend
plt.xlabel(metadata_x_axis, labelpad=20, fontsize=12)
plt.ylabel(rna_conc_y_axis, labelpad=20, fontsize=12)
plt.title(f'{rna_conc_y_axis} by Elution Plate #', fontsize=16, pad=10)
plt.legend()

rna_conc_maximum = metadata_df["Eluted RNA conc (ng/ul)"].max()
y_axis_maximum = math.ceil((rna_conc_maximum/5.0)*5) + 20
yticks = list(range(0,y_axis_maximum,5))
ax.set_yticks(yticks)

yticklabels = ax.get_yticklabels()
for i, label in enumerate(yticklabels):
    if i % 2 != 0:  # Check if the index is odd
        label.set_visible(False)

elution_rna_conc_plot = plt.gcf()

# BACKDILUTED RNA CONC BOXPLOT GENERATION
metadata_x_axis = "Backdilution Plate #"
backdilution_conc_y_axis = "Backdiluted RNA conc (ng/ul)"

fig_size_x_dimension = 2.5*source_plate_count
fig, ax = plt.subplots(figsize=(fig_size_x_dimension, 10))  # Set a larger height by adjusting the second value (height) in figsize
sns.boxplot(x=metadata_x_axis, y=backdilution_conc_y_axis, data=metadata_df, color='grey')
sns.stripplot(x=metadata_x_axis, y=backdilution_conc_y_axis, data=metadata_df, color='black', size=8, jitter=True)

plt.axhline(y=norm_conc_1, color='red', linestyle='--', linewidth=2, xmin=0,xmax=0.25, label='Backdilution normalization target')
ax.text(0, norm_conc_1, f'{norm_conc_1} ng/ul', color='black', backgroundcolor='white', ha='center', va='center', bbox=dict(facecolor='white', edgecolor='white', boxstyle='round,pad=0.5'))
if source_plate_count > 1:
    plt.axhline(y=norm_conc_2, color='red', linestyle='--', xmin=0.25,xmax=0.50)
    ax.text(1, norm_conc_2, f'{norm_conc_2} ng/ul', color='black', backgroundcolor='white', ha='center', va='center', bbox=dict(facecolor='white', edgecolor='white', boxstyle='round,pad=0.5'))
if source_plate_count > 2:
    plt.axhline(y=norm_conc_3, color='red', linestyle='--', xmin=0.50,xmax=0.75)
    ax.text(2, norm_conc_3, f'{norm_conc_3} ng/ul', color='black', backgroundcolor='white', ha='center', va='center', bbox=dict(facecolor='white', edgecolor='white', boxstyle='round,pad=0.5'))
if source_plate_count > 3:
    plt.axhline(y=norm_conc_4, color='red', linestyle='--', xmin=0.75,xmax=1.0)
    ax.text(3, norm_conc_4, f'{norm_conc_4} ng/ul', color='black', backgroundcolor='white', ha='center', va='center', bbox=dict(facecolor='white', edgecolor='white', boxstyle='round,pad=0.5'))

# Set labels and legend
plt.xlabel(metadata_x_axis, labelpad=20, fontsize=12)
plt.ylabel(backdilution_conc_y_axis, labelpad=20, fontsize=12)
plt.title(f'{backdilution_conc_y_axis} by Backdilution Plate #', fontsize=16, pad=10)
plt.legend()

backdilution_conc_maximum = metadata_df["Backdiluted RNA conc (ng/ul)"].max()
y_axis_maximum = math.ceil((backdilution_conc_maximum/5.0)*5) + 20
yticks = list(range(0,y_axis_maximum,5))
ax.set_yticks(yticks)

yticklabels = ax.get_yticklabels()
for i, label in enumerate(yticklabels):
    if i % 2 != 0:  # Check if the index is odd
        label.set_visible(False)

backdilution_conc_plot = plt.gcf()

# BACKDILUTION RATE PIECHART GENERATION
metadata_df_grouped = metadata_df.groupby("Backdilution Plate #")
plate_1_df = metadata_df_grouped.get_group('Backdilution plate[001]')
plate_1_zero_backdilution_volume_rows = plate_1_df[(plate_1_df['Backdilution volume needed for normalization (ul)'] == 0)]
plate_1_nonzero_backdilution_volume_rows = plate_1_df[(plate_1_df['Backdilution volume needed for normalization (ul)'] != 0)]
plate_1_backdilution_rate = round(len(plate_1_nonzero_backdilution_volume_rows)/len(plate_1_df)*100, 1)
plate_1_undilute_rate = round(len(plate_1_zero_backdilution_volume_rows)/len(plate_1_df)*100, 1)

labels = ['Backdiluted samples','Undiluted samples']
percentages = [plate_1_backdilution_rate, plate_1_undilute_rate]
plt.figure()
plt.pie(percentages, labels=labels, autopct='%1.1f%%', startangle=90, colors=['green','red'])
plt.title('Backdilution plate[001] dilution rate', fontsize=16)
plate_1_backdilution_piechart = plt.gcf()

if source_plate_count > 1:
    plate_2_df = metadata_df_grouped.get_group('Backdilution plate[002]')
    plate_2_zero_backdilution_volume_rows = plate_2_df[(plate_2_df['Backdilution volume needed for normalization (ul)'] == 0)]
    plate_2_nonzero_backdilution_volume_rows = plate_2_df[(plate_2_df['Backdilution volume needed for normalization (ul)'] != 0)]
    plate_2_backdilution_rate = round(len(plate_2_nonzero_backdilution_volume_rows)/len(plate_2_df)*100, 1)
    plate_2_undilute_rate = round(len(plate_2_zero_backdilution_volume_rows)/len(plate_2_df)*100, 1)
    
    labels = ['Backdiluted samples','Undiluted samples']
    percentages = [plate_2_backdilution_rate,plate_2_undilute_rate]
    plt.figure()
    plt.pie(percentages, labels=labels, autopct='%1.1f%%', startangle=90, colors=['green','red'])
    plt.title('Backdilution plate[002] dilution rate',fontsize=16)
    plate_2_backdilution_piechart = plt.gcf()
    
if source_plate_count > 2:
    plate_3_df = metadata_df_grouped.get_group('Backdilution plate[003]')
    plate_3_zero_backdilution_volume_rows = plate_3_df[(plate_3_df['Backdilution volume needed for normalization (ul)'] == 0)]
    plate_3_nonzero_backdilution_volume_rows = plate_3_df[(plate_3_df['Backdilution volume needed for normalization (ul)'] != 0)]
    plate_3_backdilution_rate = round(len(plate_3_nonzero_backdilution_volume_rows)/len(plate_3_df)*100, 1)
    plate_3_undilute_rate = round(len(plate_3_zero_backdilution_volume_rows)/len(plate_3_df)*100, 1)
    
    labels = ['Backdiluted samples','Undiluted samples']
    percentages = [plate_3_backdilution_rate,plate_3_undilute_rate]
    plt.figure()
    plt.pie(percentages, labels=labels, autopct='%1.1f%%', startangle=90, colors=['green','red'])
    plt.title('Backdilution plate[003] dilution rate',fontsize=16)
    plate_3_backdilution_piechart = plt.gcf()
    
if source_plate_count > 3:
    plate_4_df = metadata_df_grouped.get_group('Backdilution plate[004]')
    plate_4_zero_backdilution_volume_rows = plate_4_df[(plate_4_df['Backdilution volume needed for normalization (ul)'] == 0)]
    plate_4_nonzero_backdilution_volume_rows = plate_4_df[(plate_4_df['Backdilution volume needed for normalization (ul)'] != 0)]
    plate_4_backdilution_rate = round(len(plate_4_nonzero_backdilution_volume_rows)/len(plate_4_df)*100, 1)
    plate_4_undilute_rate = round(len(plate_4_zero_backdilution_volume_rows)/len(plate_4_df)*100, 1)
    
    labels = ['Backdiluted samples','Undiluted samples']
    percentages = [plate_4_backdilution_rate,plate_4_undilute_rate]
    plt.figure()
    plt.pie(percentages, labels=labels, autopct='%1.1f%%', startangle=90, colors=['green','red'])
    plt.title('Backdilution plate[004] dilution rate',fontsize=16)
    plate_4_backdilution_piechart = plt.gcf()
    
# SAVE ALL PLOTS TO A SINGLE PDF FILE
current_time = datetime.now()
reformatted_datetime_string = current_time.strftime("%Y-%m-%d %H-%M-%S")
plot_filename = f"{reformatted_datetime_string}_RNA Prep Data Dashboard.pdf"

pp = PdfPages(plot_file_path + plot_filename)
fig_nums = plt.get_fignums()
figs = [plt.figure(n) for n in fig_nums]
for fig in figs:
    fig.savefig(pp, format='pdf')
pp.close()