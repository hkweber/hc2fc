from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


class MultiDataProcessor:
    """
    Calculates Q-U data of full cell based on two filtered half cell datasets from the anode and cathode filebrowser and stores it in the full-cell databrowser.
    """
    def __init__(self, app_context):
        self.app = app_context

    def get_dataset_by_name(self, dataset_name, dataset_type):
        """
        Retrieve the dataset by name from the stored filtered datasets.
        """
        datasets = self.app.data_manager.filtered_datasets.get(dataset_type, [])
        for dataset in datasets:
            if dataset["name"] == dataset_name:
                return dataset["data"]
        return None

    def calculate_full_cell_voltage(self):
        # Get selected datasets
        anode_datasets = self.app.anode_browser.get_selected_datasets()
        cathode_datasets = self.app.cathode_browser.get_selected_datasets()

        if len(anode_datasets) != 1 or len(cathode_datasets) != 1:
            messagebox.showerror("Error", "Please select exactly one dataset from each browser.")
            return

        anode_data = self.get_dataset_by_name(anode_datasets[0], "anode")
        cathode_data = self.get_dataset_by_name(cathode_datasets[0], "cathode")

        if anode_data is None or cathode_data is None:
            messagebox.showerror("Error", "Selected datasets are invalid.")
            return

        # Filter discharge for anode and charge for cathode
        anode_discharge = anode_data[anode_data["Command"].str.contains("Discharge", na=False)]
        cathode_charge = cathode_data[cathode_data["Command"].str.contains("Charge", na=False)]

        if anode_discharge.empty or cathode_charge.empty:
            messagebox.showerror("Error", "Selected datasets do not contain the required half-cycle data.")
            return

        # Generate common Q range
        common_q = np.linspace(
            max(anode_discharge["Ah-Cyc-Discharge-0"].min(), cathode_charge["Ah-Cyc-Charge-0"].min()),
            min(anode_discharge["Ah-Cyc-Discharge-0"].max(), cathode_charge["Ah-Cyc-Charge-0"].max()),
            500  # Generate 500 evenly spaced Q points
        )

        # Use linear spline for U values
        anode_spline = self.app.data_manager.compute_linear_spline(anode_discharge["Ah-Cyc-Discharge-0"], anode_discharge["U[V]"])
        cathode_spline = self.app.data_manager.compute_linear_spline(cathode_charge["Ah-Cyc-Charge-0"], cathode_charge["U[V]"])

        if not anode_spline or not cathode_spline:
            messagebox.showerror("Error", "Failed to compute linear splines for one or both datasets.")
            return

        anode_u = np.interp(common_q, anode_spline["x"], anode_spline["y"])
        cathode_u = np.interp(common_q, cathode_spline["x"], cathode_spline["y"])

        # Calculate full cell voltage (difference between cathode and anode)
        full_cell_u = cathode_u - anode_u

        # Create a new dataset
        full_cell_data = pd.DataFrame({
            "Q (Ah)": common_q,
            "U_full_cell (V)": full_cell_u
        })
        dataset_name = f"Full_Cell_{anode_datasets[0]}_+_{cathode_datasets[0]}"
        self.app.data_manager.filtered_datasets.setdefault("full_cell", []).append({"name": dataset_name, "data": full_cell_data})
        self.app.full_cell_browser.add_dataset(dataset_name)  # Add to full cell browser

        messagebox.showinfo("Success", f"Full cell dataset created: {dataset_name}")
