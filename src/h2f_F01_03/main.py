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
    #    self.filter_widgets = {}  # Initialize dictionary to store widgets
        self.multi_data_processor = MultiDataProcessor(self)
        self.data_manager = DataManager(self)  # Initialize DataManager
        self._initialize_ui()
        self.project_manager = ProjectManager(self)  # Initialize ProjectManager    

    def _initialize_ui(self):
        """ Initialize the main UI layout. """
        self._setup_main_container()
        self._create_project_section()
        self._create_single_data_sections()
        self._create_browser_sections()
        self._create_full_cell_voltage_button()
        self._create_multigraph_plotter()
        self.data_manager.dummy

    def _setup_main_container(self):
        """ Set up a fully scrollable main container for the UI. """
        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container)
        
        # Add vertical scrollbar
        self.v_scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.v_scrollbar.pack(side="right", fill="y")

        # Add horizontal scrollbar
        self.h_scrollbar = tk.Scrollbar(container, orient="horizontal", command=self.canvas.xview)
        self.h_scrollbar.pack(side="bottom", fill="x")

        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        self.main_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        self.main_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # ✅ Enable mouse scrolling inside the main frame
        self.main_frame.bind("<Enter>", self._bind_mouse_scroll)
        self.main_frame.bind("<Leave>", self._unbind_mouse_scroll)

    def _bind_mouse_scroll(self, event):
        """ Enables scrolling with the mouse wheel when hovering over the main frame. """
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_scroll)  # Windows & MacOS Vertical Scroll
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_mouse_scroll)  # ✅ Horizontal Scroll
        self.canvas.bind_all("<Button-4>", self._on_mouse_scroll)  # Linux Vertical Scroll Up
        self.canvas.bind_all("<Button-5>", self._on_mouse_scroll)  # Linux Vertical Scroll Down

    def _unbind_mouse_scroll(self, event):
        """ Disables mouse scrolling when leaving the scrollable area. """
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Shift-MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mouse_scroll(self, event):
        """ Handles mouse scroll events for both vertical and horizontal scrolling. """
        if event.state & 0x0001:  # ✅ Shift key is held -> Scroll horizontally
            if event.num == 4 or event.delta > 0:  # Scroll left
                self.canvas.xview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:  # Scroll right
                self.canvas.xview_scroll(1, "units")
        else:  # Normal vertical scrolling
            if event.num == 4 or event.delta > 0:  # Scroll up
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:  # Scroll down
                self.canvas.yview_scroll(1, "units")
    
### Project section

    def _create_project_section(self):
        project_frame = tk.LabelFrame(self.main_frame, text="project section", font=UIStyling.LABEL_FONT)
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

    def _create_single_data_sections(self):
        """
        creates anode, cathode and full-cell single data sections 
        """
        self.is_single_data_section_visible = True  # ✅ Track visibility state

        # Create a frame for the toggle button
        toggle_frame = tk.Frame(self.main_frame)
        toggle_frame.pack(fill="x", padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        # ✅ Button to toggle visibility
        self.toggle_button = tk.Button(
            toggle_frame, text="Hide Data Modification Section", 
            command=self._toggle_hide_single_data_section, font=UIStyling.BUTTON_FONT
        )
        self.toggle_button.pack(side="left", padx=UIStyling.FRAME_PADX)

### create a frame for singe data operations on a electrode type

        self.single_data_section_frame = tk.LabelFrame(self.main_frame, text="data modification section", font=UIStyling.LABEL_FONT)
        self.single_data_section_frame.pack(fill="x", padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        self._create_single_data_section("anode")
        self._create_single_data_section("cathode")
        self._create_single_data_section("full_cell")
    
    def _toggle_hide_single_data_section(self):
        """ Toggles visibility of the single data section without affecting the UI layout. """
        if self.is_single_data_section_visible:
            # ✅ Replace section with an empty frame (prevents other sections from shifting)
            self.empty_placeholder = tk.Frame(self.main_frame, height=1)
        #    self.empty_placeholder = tk.Frame(self.main_frame, height=50)
            self.empty_placeholder.pack(before=self.browser_section_frame, fill="x", padx=10, pady=10)

            self.single_data_section_frame.pack_forget()  # ✅ Hide section
            self.toggle_button.config(text="Show Data Modification Section")
        else:
            # ✅ Remove placeholder & restore section in the correct order
            self.empty_placeholder.pack_forget()
            self.single_data_section_frame.pack(before=self.browser_section_frame, fill="x", padx=10, pady=10)

            self.toggle_button.config(text="Hide Data Modification Section")

        self.is_single_data_section_visible = not self.is_single_data_section_visible

### create single data section

    def _create_single_data_section(self, electrode_name):
        """
        creates a frame that contains all single data operations for an electrode type 
        """

        ### create a frame for singe data operations on a electrode type
        single_data_frame = tk.LabelFrame(self.single_data_section_frame, text=electrode_name, font=UIStyling.LABEL_FONT)
        single_data_frame.pack(side= "left", fill="x", padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        ### electrode data import section
        electrode_file_frame = tk.Frame(single_data_frame)
        electrode_file_frame.pack(side="top", fill="both", expand=True, padx=UIStyling.FRAME_PADX)
        # electrode_file_frame.pack(side="left", fill="both", expand=True, padx=UIStyling.FRAME_PADX)

        self.electrode_widget = DataWidget(electrode_file_frame, electrode_name, electrode_name, self.data_manager)
        self.electrode_widget.frame.pack(fill="x", expand=True)
       
        ### Creates the Data Filtering section
        electrode_filter_frame = tk.Frame(single_data_frame)
        electrode_filter_frame.pack(side="left", fill="both", expand=True, padx=UIStyling.FRAME_PADX)

        if not hasattr(self, "filter_widgets"):  
            self.filter_widgets = {}  # Initialize dictionary to store widgets

    #    if not hasattr(self, "filter_widgets"):  
    #        self.filter_widgets = {}  # Initialize dictionary to store widgets

        filter_widget = FilterWidget(single_data_frame, f"Filter {electrode_name} Data", electrode_name, self)
        self.filter_widgets[electrode_name] = filter_widget  # ✅ Store filter widget

        # Ensure filter widgets update when data is loaded
        self.data_manager.on_data_loaded_callback = self._update_filter_widgets
        
        ### Creates the Data Processing section with separate frames for electrode Key Values & Modify Electrode Data
        data_processing_frame = tk.LabelFrame(single_data_frame, text="Data Processing", font=UIStyling.LABEL_FONT)
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

    def _create_browser_sections(self):
        """
        creates anode, cathode and full-cell single data sections 
        """
### create a frame for singe data operations on a electrode type

        self.browser_section_frame = tk.LabelFrame(self.main_frame, text="browser section", font=UIStyling.LABEL_FONT)
        self.browser_section_frame.pack(fill="x", padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        self._create_browser_section("anode")
        self._create_browser_section("cathode")
        self._create_browser_section("full_cell")

### create browser section

    def _create_browser_section(self, electrode_name):
        """
        creates a frame that contains electrode browsers 
        """
        electrode_browser_frame = tk.LabelFrame(self.browser_section_frame, text=electrode_name, font=UIStyling.LABEL_FONT)
        electrode_browser_frame.pack(side="left", fill="x", expand=True, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        # create data browsers for anode, cathode and half_cell
        if not hasattr(self, "data_browsers"):
            self.data_browsers = {}  # ✅ Ensure dictionary exists

        browser = FilteredDataBrowser(electrode_browser_frame, f"Filtered {electrode_name.capitalize()} Data Browser", electrode_name, self)
        self.data_browsers[electrode_name] = browser

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

# Extract from filter widget -- these functions should be added for the other UI-Widgets, too!
    def get_filter_options(self, dataset_type):
        """
        Extracts all selected filter options for the given dataset type
        and returns them as a dictionary.
        """
        widget = self.filter_widgets.get(dataset_type)
        if not widget:
            return {}

        return {
            "remove_pause": widget.remove_pause.get(),
            "select_cycle": widget.select_cycle.get(),
            "selected_cycle": widget.cycle_selection.get(),
            "cycle_column": widget.cycle_column.get(),
            "select_charge_half_cycle": widget.select_charge_half_cycle.get(),
            "select_discharge_half_cycle": widget.select_discharge_half_cycle.get(),
            "apply_step_change": widget.apply_step_change.get(),
            "step_change_column": widget.step_change_column.get(),
            "apply_range_filter": widget.apply_range_filter.get(),
            "selected_column": widget.selected_column.get(),
            "min_value": widget.min_value.get(),
            "max_value": widget.max_value.get(),
            "fit_option": widget.fit_option.get(),
            "use_step_size": widget.use_step_size.get(),
            "step_size_value": widget.step_size_value.get(),
            "plot_option": widget.plot_option.get(),
            "data_type_selection": widget.data_type_selection.get(),
        }

if __name__ == "__main__":
    root = tk.Tk()
    app = HC2FCApp(root)
    root.mainloop()
