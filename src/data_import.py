# Import the necessary libraries
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

def import_data(file_path):
    # Read file to determine metadata lines
    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
        lines = file.readlines()
    
    # Determine number of metadata lines to skip
    skip_lines = sum(1 for line in lines if line.startswith("~"))
    
    # Read data into DataFrame, skipping metadata lines
    data = pd.read_csv(file_path, skiprows=skip_lines, delimiter=',', encoding='utf-8', on_bad_lines='skip')
    
    # Rename columns for convenience
    data = data.rename(columns=lambda x: x.strip())  # Remove any leading/trailing whitespace from column names
    columns_to_rename = {
        'Time[h]': 'Time',
        'U[V]': 'Voltage',
        'I[A]': 'Current',
        'Ah[Ah]': 'Charge_Ah',
        'Wh[Wh]': 'Energy_Wh',
        'T1[°C]': 'Temperature'
    }
    data = data.rename(columns=columns_to_rename)
    return data



# Import real dataset
file_path = "data/s2_c4_hc_graphite_form.txt"  # Update with your dataset path
data = import_data(file_path)

# Display first few rows of the dataset
print(data.head())

# Plot Time vs Voltage
plt.figure(figsize=(10, 6))
plt.plot(data['Time'], data['Voltage'], label='Voltage')
plt.xlabel('Time (hours)')
plt.ylabel('Voltage (V)')
plt.title('Time vs Voltage (Real Dataset)')
plt.legend()
plt.grid(True)
plt.show()
