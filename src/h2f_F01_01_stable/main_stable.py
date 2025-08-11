import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageTk
# from data_handling import ModifyDataWidget, FilterWidget, KeyValuesWidget
from ui_widgets import ModifyDataWidget, FilterWidget, KeyValuesWidget, DataWidget, FilteredDataBrowser
from project_management import ProjectManager
from data_management import DataManager
from multidata_management import MultiDataProcessor
from plotting import MultiGraphPlotter
from styles import UIStyling

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
        
        self.multi_data_processor = MultiDataProcessor(self)
        self.data_manager = DataManager(self)  # Initialize DataManager
        self._initialize_ui()
        self.project_manager = ProjectManager(self)  # Initialize ProjectManager

    def _initialize_ui(self):
        """ Initialize the main UI layout. """
        self._setup_main_container()
        self._create_project_section()
        self._create_electrode_sections()
#        self._create_single_data_section("anode")
#        self._create_single_data_section("cathode")
#        self._create_data_import_section()
#        self._create_filter_section()
#        self._create_data_processing_section()
#        self._create_browser_section()
#        self._create_full_cell_voltage_button()
#        self._create_multigraph_plotter()

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

### Project section

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

    def _create_electrode_sections(self):
        """
        creates anode, cathode and full-cell single data sections 
        """
### create a frame for singe data operations on a electrode type

        self.electrode_section_frame = tk.LabelFrame(self.main_frame, text="electrode section frame", font=UIStyling.LABEL_FONT)
        self.electrode_section_frame.pack(fill="x", padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)
#        self.electrode_section_frame = tk.Frame(electrode_section_frame)
#        self.electrode_section_frame.pack(side="left", fill="both", expand=True, padx=UIStyling.FRAME_PADX)

        self._create_single_data_section("anode")
        self._create_single_data_section("cathode")


### create single data section

    def _create_single_data_section(self, electrode_name):
        """
        creates a frame that contains all single data operations for an electrode type 
        """

### create a frame for singe data operations on a electrode type

        electrode_frame = tk.LabelFrame(self.electrode_section_frame, text=electrode_name, font=UIStyling.LABEL_FONT)
        electrode_frame.pack(side= "left", fill="x", padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

### electrode data import section

        electrode_file_frame = tk.Frame(electrode_frame)
        electrode_file_frame.pack(side="top", fill="both", expand=True, padx=UIStyling.FRAME_PADX)

        self.electrode_widget = DataWidget(electrode_file_frame, electrode_name, electrode_name, self.data_manager)
        self.electrode_widget.frame.pack(fill="both", expand=True)
       
### Creates the Data Filtering section

        filter_section = tk.LabelFrame(electrode_frame, text="Data Filtering", font=UIStyling.LABEL_FONT)
        filter_section.pack(side= "top", fill="both", padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        # **electrode Filtering Frame**
        electrode_filter_frame = tk.Frame(filter_section)
        electrode_filter_frame.pack(side="left", fill="both", expand=True, padx=UIStyling.FRAME_PADX)

        if not hasattr(self, "filter_widgets"):  
            self.filter_widgets = {}  # Initialize dictionary to store widgets

        filter_widget = FilterWidget(filter_section, f"Filter {electrode_name} Data", electrode_name, self)
        self.filter_widgets[electrode_name] = filter_widget  # ✅ Store filter widget

        # Ensure filter widgets update when data is loaded
        self.data_manager.on_data_loaded_callback = self._update_filter_widgets
        

### Creates the Data Processing section with separate frames for electrode Key Values & Modify Electrode Data

        data_processing_frame = tk.LabelFrame(electrode_frame, text="Data Processing", font=UIStyling.LABEL_FONT)
        data_processing_frame.pack(fill="x", padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        # **electrode Processing Frame**
        electrode_processing_frame = tk.Frame(data_processing_frame)
        electrode_processing_frame.pack(side="left", fill="both", expand=True, padx=UIStyling.FRAME_PADX)

        # Initialize storage for key values widgets if not already present 
        if not hasattr(self, "key_values_widgets"):  
            self.key_values_widgets = {}  

        key_values_widget = KeyValuesWidget(electrode_processing_frame, f"Extract {electrode_name.capitalize()} Key Values", electrode_name, self)
        key_values_widget.frame.pack(side="left", padx=UIStyling.FRAME_PADX)

        self.key_values_widgets[electrode_name] = key_values_widget

        # Initialize storage for widgets if not already present 
        if not hasattr(self, "modify_widgets"):  
            self.modify_widgets = {}  

        modify_widget = ModifyDataWidget(electrode_processing_frame, f"Modify {electrode_name.capitalize()} Data", electrode_name, self)
        modify_widget.frame.pack(side="left", padx=UIStyling.FRAME_PADX)
        self.modify_widgets[electrode_name] = modify_widget  # ✅ Store modify widget

### Creates a section for displaying filtered data browsers.
        
        browser_frame = tk.LabelFrame(electrode_frame, text="Filtered Data Browsers", font=UIStyling.LABEL_FONT)
        browser_frame.pack(fill="x", padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        electrode_frame = tk.Frame(browser_frame)
        electrode_frame.pack(side="left", fill="both", expand=True, padx=UIStyling.PAD_X)

        if not hasattr(self, "data_browsers"):
            self.data_browsers = {}  # ✅ Ensure dictionary exists

        browser = FilteredDataBrowser(browser_frame, f"Filtered {electrode_name.capitalize()} Data Browser", electrode_name, self)
        self.data_browsers[electrode_name] = browser

#        self.electrode_browser = FilteredDataBrowser(electrode_frame, "Filtered electrode Data Browser", electrode_name, self)


### Multidata analysis section

    def _create_full_cell_voltage_button(self):
        """ Add button to calculate full cell voltage. """
        tk.Button(
            self.main_frame, 
            text="Calculate Full Cell Voltage", 
            command=self.multi_data_processor.calculate_full_cell_voltage,
            font=UIStyling.BUTTON_FONT
        ).pack(pady=UIStyling.PAD_Y)

    def _create_multigraph_plotter(self):
        """ Initialize the multi-graph plotter UI. """
        multi_graph_frame = tk.Frame(self.main_frame)
        multi_graph_frame.pack(pady=UIStyling.PAD_Y)

        self.multi_graph_plotter = MultiGraphPlotter(self)
        self.multi_graph_plotter.create_ui(multi_graph_frame)  # Now it's inside MultiGraphPlotter!

# other

    def _update_filter_widgets(self):
        """ Updates filter widgets when a dataset is loaded. """
        for electrode in ["anode", "cathode"]:
            if electrode in self.filter_widgets and self.data_manager.datasets.get(electrode, {}).get("data") is not None:
                columns = self.data_manager.datasets[electrode]["data"].columns.tolist()
                self.filter_widgets[electrode].update_column_dropdown(columns)

            if electrode in self.modify_widgets and self.data_manager.datasets.get(electrode, {}).get("data") is not None:
                columns = self.data_manager.datasets[electrode]["data"].columns.tolist()
                self.modify_widgets[electrode].update_column_options(columns)


if __name__ == "__main__":
    root = tk.Tk()
    app = HC2FCApp(root)
    root.mainloop()
