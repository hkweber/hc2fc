import pandas as pd

# Path to the metadata file
metadata_file = "data/cells_meta_2.xlsx"

# Load all sheets from the Excel file
metadata_sheets = pd.read_excel(metadata_file, sheet_name=None)

# Access individual sheets by their names
for sheet_name, sheet_data in metadata_sheets.items():
    print(f"Metadata from sheet: {sheet_name}")
    print(sheet_data.head())
