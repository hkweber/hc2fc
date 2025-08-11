import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class FilterWidget:
    """
    Widget for handling filter options and visualization types.
    """
    def __init__(self, parent, label_text, dataset_type):
        self.frame = tk.LabelFrame(parent, text=label_text, font=("Arial", 10))
        self.frame.pack(pady=10, padx=20, fill="x", expand=False)

        self.dataset_type = dataset_type
        self.remove_pause = tk.BooleanVar()
        self.select_cycle = tk.BooleanVar()
        self.select_charge_half_cycle = tk.BooleanVar()
        self.select_discharge_half_cycle = tk.BooleanVar()
        self.plot_option = tk.StringVar(value="U-t")
        self.fit_option = tk.StringVar(value="no fit")
        self.visualize_key_values = tk.BooleanVar(value=False)
        self.show_cycles = tk.BooleanVar(value=False)

        self._create_filter_options()

    def _create_filter_options(self):
        # Filter Criteria
        filter_frame = tk.LabelFrame(self.frame, text="Select filter criteria", font=("Arial", 10))
        filter_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        tk.Checkbutton(filter_frame, text="Remove pause", variable=self.remove_pause).pack(anchor="w", padx=5, pady=2)
        tk.Checkbutton(filter_frame, text="Select cycle", variable=self.select_cycle).pack(anchor="w", padx=5, pady=2)
        tk.Checkbutton(filter_frame, text="Select charge half cycle", variable=self.select_charge_half_cycle).pack(anchor="w", padx=5, pady=2)
        tk.Checkbutton(filter_frame, text="Select discharge half cycle", variable=self.select_discharge_half_cycle).pack(anchor="w", padx=5, pady=2)

        # Plot Type Selection
        plot_frame = tk.LabelFrame(self.frame, text="Select plot type", font=("Arial", 10))
        plot_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        tk.Radiobutton(plot_frame, text="U vs t (Voltage-Time)", variable=self.plot_option, value="U-t").pack(anchor="w", padx=5)
        tk.Radiobutton(plot_frame, text="I vs t (Current-Time)", variable=self.plot_option, value="I-t").pack(anchor="w", padx=5)
        tk.Radiobutton(plot_frame, text="Q vs U (Charge-Voltage)", variable=self.plot_option, value="Q-U").pack(anchor="w", padx=5)

        # Fit Type Selection
        fit_frame = tk.LabelFrame(self.frame, text="Select fit type", font=("Arial", 10))
        fit_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        
        tk.Radiobutton(fit_frame, text="No Fit", variable=self.fit_option, value="no fit").pack(anchor="w", padx=5)
        tk.Radiobutton(fit_frame, text="Linear Spline", variable=self.fit_option, value="linear spline").pack(anchor="w", padx=5)

        # Visualization Options
        visualization_frame = tk.LabelFrame(self.frame, text="Select visualization type", font=("Arial", 10))
        visualization_frame.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")
        
        tk.Checkbutton(visualization_frame, text="Show Key Values", variable=self.visualize_key_values).pack(anchor="w", padx=5)
        tk.Checkbutton(visualization_frame, text="Show Cycles", variable=self.show_cycles).pack(anchor="w", padx=5)

class DataWidget:
    """
    Widget for handling file operations and plotting for anode/cathode datasets.
    """
    def __init__(self, parent, label_text, dataset_key, app_context):
        self.app_context = app_context
        self.dataset_key = dataset_key

        self.frame = tk.Frame(parent, relief="groove", borderwidth=2)
        self.frame.grid(pady=10, padx=20, row=0, column=0 if dataset_key == "anode" else 1, sticky="nsew")

        # File Operations
        tk.Label(self.frame, text=f"{label_text} file:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.file_label = tk.Label(self.frame, textvariable=self.app_context.datasets[dataset_key]["file_path"], width=40, anchor="w")
        self.file_label.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        tk.Button(self.frame, text="Load", command=self._load_file).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(self.frame, text="Show Data Table", command=self._show_data_table).grid(row=0, column=3, padx=5, pady=5)
        tk.Button(self.frame, text="Plot Data", command=self._plot_data).grid(row=0, column=4, padx=5, pady=5)

    def _load_file(self):
        self.app_context.select_file(self.dataset_key)

    def _show_data_table(self):
        self.app_context.show_data_table(self.dataset_key)

    def _plot_data(self):
        self.app_context.plot_data(self.dataset_key)

class HC2FCApp:
    """
    Main Application Class for hc2fc.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("hc2fc")
        self.root.geometry("800x600")

        # Datasets dictionary
        self.datasets = {
            "anode": {"data": None, "file_path": tk.StringVar(value="No file selected")},
            "cathode": {"data": None, "file_path": tk.StringVar(value="No file selected")},
        }

        self._initialize_ui()

    def _initialize_ui(self):
        # Main container frame with scrollbar
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

        # Title
        tk.Label(self.main_frame, text="hc2fc", font=("Arial", 16, "bold")).pack(pady=10)

        # Half Cell Data Section
        tk.Label(self.main_frame, text="Half cell data", font=("Arial", 12, "underline")).pack(pady=5)
        data_section = tk.Frame(self.main_frame)
        data_section.pack(fill="x")
        data_section.grid_columnconfigure(0, weight=1)
        data_section.grid_columnconfigure(1, weight=1)

        self.anode_widget = DataWidget(data_section, "Anode", "anode", self)
        self.cathode_widget = DataWidget(data_section, "Cathode", "cathode", self)

        # Filter Sections
        filter_section = tk.Frame(self.main_frame)
        filter_section.pack(fill="x")
        filter_section.grid_columnconfigure(0, weight=1)
        filter_section.grid_columnconfigure(1, weight=1)

        self.anode_filter_widget = FilterWidget(filter_section, "Filter Anode Data", "anode")
        self.cathode_filter_widget = FilterWidget(filter_section, "Filter Cathode Data", "cathode")

        # Full Cell Data Section
        tk.Label(self.main_frame, text="Full cell data section", font=("Arial", 12, "underline")).pack(pady=5)
        tk.Button(self.main_frame, text="Plot Prediction", command=self._plot_full_cell_prediction).pack(pady=10)

    # Reuse existing methods like select_file, show_data_table, etc.

    def _plot_full_cell_prediction(self):
        # TODO: Implement full cell prediction logic
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = HC2FCApp(root)
    root.mainloop()
