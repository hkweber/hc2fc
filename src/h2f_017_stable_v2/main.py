import os
import io
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import zipfile
import json
import pickle
from PIL import Image, ImageTk
from data_handling import ModifyDataWidget, FilterWidget, KeyValuesWidget
from plotting import MultiGraphPlotter
from ui_widgets import DataWidget, FilteredDataBrowser
from styles import UIStyling
from project_management import ProjectManager
from data_management import DataManager

class HC2FCApp:
    """
    Main Application Class for hc2fc.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("hc2fc")
        self.root.geometry("800x600")

        # Add multi-plot type attribute
        self.multi_plot_type = tk.StringVar(value="U-t (Voltage-Time)")

        self.data_manager = DataManager(self)  # Initialize DataManager
        self._initialize_ui()
        self.project_manager = ProjectManager(self)  # Initialize ProjectManager

        # Debugging: Print all attributes of self.app
        print("Attributes of self.app (HC2FCApp):")
        print(dir(self))

    def _initialize_ui(self):
        """ Initialize the main UI layout. """
        self._setup_main_container()
        self._create_project_section()
        self._create_data_import_section()
        self._create_filter_section()
        self._create_data_processing_section()
        self._create_browser_section()
        self._create_full_cell_voltage_button()
        self._create_multigraph_plotter()

    def _setup_main_container(self):
        """ Set up a scrollable main container for the UI. """
        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container)
        self.scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.main_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        self.main_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
    
    def _create_project_section(self):
        project_frame = tk.LabelFrame(self.main_frame, text="Project Management", font=UIStyling.LABEL_FONT)
        project_frame.pack(fill="x", padx=UIStyling.PAD_X, pady=UIStyling.PAD_Y)

        tk.Button(project_frame, text="Save Project",
                command=lambda: self.project_manager.save_project_callback(),
                font=UIStyling.BUTTON_FONT).pack(side="left", padx=UIStyling.PAD_X)

        tk.Button(project_frame, text="Load Project",
                command=lambda: self.project_manager.load_project_callback(),
                font=UIStyling.BUTTON_FONT).pack(side="left", padx=UIStyling.PAD_X)

        tk.Button(project_frame, text="Show Loaded Plots",
                command=lambda: self.project_manager.show_loaded_plots(),
                font=UIStyling.BUTTON_FONT).pack(side="left", padx=UIStyling.PAD_X)
        
    def _create_data_import_section(self):
        """
        Creates the Data Import section with separate frames for:
        - Anode File Selection
        - Cathode File Selection
        """
        data_import_frame = tk.LabelFrame(self.main_frame, text="Data Import", font=UIStyling.LABEL_FONT)
        data_import_frame.pack(fill="x", padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        # **Anode File Frame**
        anode_file_frame = tk.Frame(data_import_frame)
        anode_file_frame.pack(side="left", fill="both", expand=True, padx=UIStyling.FRAME_PADX)

        self.anode_widget = DataWidget(anode_file_frame, "Anode", "anode", self.data_manager)
        self.anode_widget.frame.pack(fill="both", expand=True)

        # **Cathode File Frame**
        cathode_file_frame = tk.Frame(data_import_frame)
        cathode_file_frame.pack(side="left", fill="both", expand=True, padx=UIStyling.FRAME_PADX)

        self.cathode_widget = DataWidget(cathode_file_frame, "Cathode", "cathode", self.data_manager)
        self.cathode_widget.frame.pack(fill="both", expand=True)

    def _create_filter_section(self):
        """
        Creates the Data Filtering section with separate frames for anode and cathode filtering.
        """
        filter_section = tk.LabelFrame(self.main_frame, text="Data Filtering", font=UIStyling.LABEL_FONT)
        filter_section.pack(fill="x", padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        # **Anode Filtering Frame**
        anode_filter_frame = tk.Frame(filter_section)
        anode_filter_frame.pack(side="left", fill="both", expand=True, padx=UIStyling.FRAME_PADX)

        self.anode_filter_widget = FilterWidget(anode_filter_frame, "Filter anode data", "anode", self)

        # **Cathode Filtering Frame**
        cathode_filter_frame = tk.Frame(filter_section)
        cathode_filter_frame.pack(side="left", fill="both", expand=True, padx=UIStyling.FRAME_PADX)

        self.cathode_filter_widget = FilterWidget(cathode_filter_frame, "Filter cathode data", "cathode", self)

        # Ensure filter widgets update when data is loaded
        self.data_manager.on_data_loaded_callback = self._update_filter_widgets

    def _create_data_processing_section(self):
        """
        Creates the Data Processing section with separate frames for:
        - Anode Key Values & Modify Anode Data
        - Cathode Key Values & Modify Cathode Data
        """
        data_processing_frame = tk.LabelFrame(self.main_frame, text="Data Processing", font=UIStyling.LABEL_FONT)
        data_processing_frame.pack(fill="x", padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        # **Anode Processing Frame**
        anode_processing_frame = tk.Frame(data_processing_frame)
        anode_processing_frame.pack(side="left", fill="both", expand=True, padx=UIStyling.FRAME_PADX)

        # **Anode: Extract Key Values & Modify Data (Side by Side)**
        self.anode_key_values_widget = KeyValuesWidget(anode_processing_frame, "Extract Anode Key Values", "anode", self)
        self.anode_key_values_widget.frame.pack(side="left", padx=UIStyling.FRAME_PADX)

        self.anode_modify_widget = ModifyDataWidget(anode_processing_frame, "Modify Anode Data", "anode", self)
        self.anode_modify_widget.frame.pack(side="left", padx=UIStyling.FRAME_PADX)

        # **Cathode Processing Frame**
        cathode_processing_frame = tk.Frame(data_processing_frame)
        cathode_processing_frame.pack(side="left", fill="both", expand=True, padx=UIStyling.FRAME_PADX)

        # **Cathode: Extract Key Values & Modify Data (Side by Side)**
        self.cathode_key_values_widget = KeyValuesWidget(cathode_processing_frame, "Extract Cathode Key Values", "cathode", self)
        self.cathode_key_values_widget.frame.pack(side="left", padx=UIStyling.FRAME_PADX)

        self.cathode_modify_widget = ModifyDataWidget(cathode_processing_frame, "Modify Cathode Data", "cathode", self)
        self.cathode_modify_widget.frame.pack(side="left", padx=UIStyling.FRAME_PADX)

    def _create_browser_section(self):
        """
        Creates a section for displaying filtered data browsers.
        """
        browser_frame = tk.LabelFrame(self.main_frame, text="Filtered Data Browsers", font=UIStyling.LABEL_FONT)
        browser_frame.pack(fill="x", padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        anode_frame = tk.Frame(browser_frame)
        anode_frame.pack(side="left", fill="both", expand=True, padx=UIStyling.PAD_X)

        cathode_frame = tk.Frame(browser_frame)
        cathode_frame.pack(side="left", fill="both", expand=True, padx=UIStyling.PAD_X)

        full_cell_frame = tk.Frame(browser_frame)
        full_cell_frame.pack(side="left", fill="both", expand=True, padx=UIStyling.PAD_X)

        self.anode_browser = FilteredDataBrowser(anode_frame, "Filtered Anode Data Browser", "anode", self)
        self.cathode_browser = FilteredDataBrowser(cathode_frame, "Filtered Cathode Data Browser", "cathode", self)
        self.full_cell_browser = FilteredDataBrowser(full_cell_frame, "Filtered Full Cell Data Browser", "full_cell", self)

### other methods

    def store_filtered_data(self, dataset_type):
        self.data_manager.store_filtered_data(dataset_type)

    def save_filtered_data(self, dataset_type):
        self.data_manager.save_filtered_data(dataset_type)

    def _update_filter_widgets(self):
        """ Updates filter widgets when a dataset is loaded. """
        if self.data_manager.datasets.get("anode", {}).get("data") is not None:
            columns = self.data_manager.datasets["anode"]["data"].columns.tolist()
            self.anode_filter_widget.update_column_dropdown(columns)

        if self.data_manager.datasets.get("cathode", {}).get("data") is not None:
            columns = self.data_manager.datasets["cathode"]["data"].columns.tolist()
            self.cathode_filter_widget.update_column_dropdown(columns)

### data analysis methods - multiplotter

    def _create_full_cell_voltage_button(self):
        """ Add button to calculate full cell voltage. """
        tk.Button(
            self.main_frame, 
            text="Calculate Full Cell Voltage", 
            command=self.calculate_full_cell_voltage,
            font=UIStyling.BUTTON_FONT
        ).pack(pady=UIStyling.PAD_Y)

    def calculate_full_cell_voltage(self):
        # Get selected datasets
        anode_datasets = self.anode_browser.get_selected_datasets()
        cathode_datasets = self.cathode_browser.get_selected_datasets()

        if len(anode_datasets) != 1 or len(cathode_datasets) != 1:
            messagebox.showerror("Error", "Please select exactly one dataset from each browser.")
            return

        anode_data = self._get_dataset_by_name(anode_datasets[0], "anode")
        cathode_data = self._get_dataset_by_name(cathode_datasets[0], "cathode")

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
        anode_spline = self.data_manager.compute_linear_spline(anode_discharge["Ah-Cyc-Discharge-0"], anode_discharge["U[V]"])
        cathode_spline = self.data_manager.compute_linear_spline(cathode_charge["Ah-Cyc-Charge-0"], cathode_charge["U[V]"])

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
        self.data_manager.filtered_datasets.setdefault("full_cell", []).append({"name": dataset_name, "data": full_cell_data})
        self.full_cell_browser.add_dataset(dataset_name)  # Add to full cell browser

        messagebox.showinfo("Success", f"Full cell dataset created: {dataset_name}")

    def _create_multigraph_plotter(self):
        """ Initialize the multi-graph plotter UI. """
        multi_graph_frame = tk.Frame(self.main_frame)
        multi_graph_frame.pack(pady=UIStyling.PAD_Y)

        self.multi_graph_plotter = MultiGraphPlotter(self)
        self.multi_graph_plotter.create_ui(multi_graph_frame)  # Now it's inside MultiGraphPlotter!

    def on_dataset_loaded(self, dataset_type, dataset):
        """ Ensure filter widgets are updated with column names when a dataset is loaded. """
        column_names = dataset.columns.tolist()
        
        if dataset_type == "anode":
            self.anode_filter_widget.update_column_dropdown(column_names)
        elif dataset_type == "cathode":
            self.cathode_filter_widget.update_column_dropdown(column_names)

    def _plot_multi_graph(self):
        plotter = MultiGraphPlotter(self)
        plotter.plot_multi_graph()


    def _get_dataset_by_name(self, dataset_name, dataset_type):
        """
        Retrieve the dataset by name from the stored filtered datasets.
        """
        datasets = self.data_manager.filtered_datasets.get(dataset_type, [])
        for dataset in datasets:
            if dataset["name"] == dataset_name:
                return dataset["data"]
        return None




### key values

    def compute_key_points(self, filtered_data, filter_widget, key_values_widget, plot_type):
        """
        Computes key points (e.g., max voltage, max charge, max discharge) for visualization.
        Returns a list of dictionaries containing x, y, and label data for each point.
        """
        key_points = []

        # Define a smart rounding function
        def smart_round(value):
            if value >= 0.01:
                return round(value, 2)  # Two decimal places for larger values
            return f"{value:.2e}"  # Scientific notation for small values

        # Max Voltage for U-t
        if plot_type == "U-t" and key_values_widget.extract_max_voltage.get():
            max_voltage = filtered_data["U[V]"].max()
            time_at_max_voltage = filtered_data.loc[filtered_data["U[V]"] == max_voltage, "Time[h]"].iloc[0]
            key_points.append(
                {
                    "x": time_at_max_voltage,
                    "y": max_voltage,
                    "color": "blue",
                    "marker": "o",
                    "label": f"Max Voltage: {smart_round(max_voltage)} V",
                }
            )

        # Max Current for I-t
        if plot_type == "I-t" and key_values_widget.extract_max_charge.get():  # Assuming this refers to max current
            max_current = filtered_data["I[A]"].max()
            time_at_max_current = filtered_data.loc[filtered_data["I[A]"] == max_current, "Time[h]"].iloc[0]
            key_points.append(
                {
                    "x": time_at_max_current,
                    "y": max_current,
                    "color": "orange",
                    "marker": "x",
                    "label": f"Max Current: {smart_round(max_current)} A",
                }
            )

        # Max Charge and Discharge for Q-U
        if plot_type == "Q-U":
            if key_values_widget.extract_max_charge.get() and not filter_widget.select_discharge_half_cycle.get():
                max_charge = filtered_data["Ah-Cyc-Charge-0"].max()
                voltage_at_max_charge = filtered_data.loc[filtered_data["Ah-Cyc-Charge-0"] == max_charge, "U[V]"].iloc[0]
                key_points.append(
                    {
                        "x": max_charge,
                        "y": voltage_at_max_charge,
                        "color": "green",
                        "marker": "x",
                        "label": f"Max Charge: {smart_round(max_charge)} Ah",
                    }
                )

            if key_values_widget.extract_max_discharge.get() and not filter_widget.select_charge_half_cycle.get():
                max_discharge = filtered_data["Ah-Cyc-Discharge-0"].max()
                voltage_at_max_discharge = filtered_data.loc[filtered_data["Ah-Cyc-Discharge-0"] == max_discharge, "U[V]"].iloc[0]
                key_points.append(
                    {
                        "x": max_discharge,
                        "y": voltage_at_max_discharge,
                        "color": "red",
                        "marker": "^",
                        "label": f"Max Discharge: {smart_round(max_discharge)} Ah",
                    }
                )

        return key_points

if __name__ == "__main__":
    root = tk.Tk()
    app = HC2FCApp(root)
    root.mainloop()
