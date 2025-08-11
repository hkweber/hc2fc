from data_import import import_data

# Updated file paths with new simplified names
anode_file_path = "../data/s2_c4_hc_graphite_form.txt"
cathode_file_path = "../data/s2_c8_hc_lfp_form.txt"

# Load anode and cathode data
anode_data = import_data(anode_file_path)
cathode_data = import_data(cathode_file_path)

# Print out the first few rows to verify the data
print("Anode Data:")
print(anode_data.head())

print("\nCathode Data:")
print(cathode_data.head())

