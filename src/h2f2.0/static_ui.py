### static_ui.py

import tkinter as tk
from tkinter import filedialog, messagebox

from ui_styles import UIStyling
from ui_elements import UIElements

class UI:
    """
    Static UI
    """
    def __init__(self, root):
        self.root = root
        # Initialize UI vars before initializing UI
        # Initialize UI vars for data transfromation section
        
        # filter_data_widget checkboxes 
        self.apply_range_filter = {}
        self.remove_pause = {}
        self.select_cycle = {}
        self.select_charge_half_cycle = {}
        self.select_discharge_half_cycle = {}
        self.apply_step_change = {}
        # filter_data_widget dropdowns
        self.selected_cycle = {} # 1,2,3, all
        self.selected_cycle_column = {} # Cyc-Count, abs_cycle
        self.selected_step_change_column = {} # Line, Cyc-Count ...
        
        # fit_data_widget radiobuttons
        self.fit_option = {} # no fit, linear_spline
        # fit_data_checkbox
        self.use_step_size = {} # False
        self.step_size_value = {} # 000.1 ...

        # plot_data_widget radiobuttons
        self.plot_option = {} # "U-t", "I-t" ...

        # modify_data_widget - checkbuttons
        self.compute_du_dq = {}
        self.compute_abs_cycle = {}
        self.normalize_voltage = {}
        self.apply_offset = {}
        # modify_data_widget - dropdowns
        self.selected_column = {} # U[V], ...
        # modify_data_widget - entryfield
        self.offset_value = {} # 0, ...

        # visualize_data_widget - checkbuttons
        self.visualize_key_values = {}
        self.show_cycles = {}
        # data_processing_widget - dropdown
        self.selected_data_type = {} # Modified Data
         
        # Initialize UI
        self._initialize_ui()

    def _initialize_ui(self):
        """ Initialize the main UI layout. """
        self._setup_main_container()
        self._create_project_section()
        self._create_data_transformation_section()

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

    def _create_project_section(self):
        ''' Section for saving and loading projects'''
        project_section_frame = UIElements.section_frame(self.main_frame, "project section")
        
        UIElements.button(project_section_frame, "Save Project",
                          command=lambda: self.project_manager.save_project_callback()) #change
        UIElements.button(project_section_frame, text="Load Project",
                          command=lambda: self.project_manager.load_project_callback()) #change

    def _create_data_transformation_section(self):
        ''' Section for transformations on single datasets for anode, cathode and full_cells'''
        self.data_transformation_sections_frame = UIElements.section_frame(self.main_frame, "data transformation section")
        self._create_data_transformation_widget("anode")
        self._create_data_transformation_widget("cathode")
        self._create_data_transformation_widget("full_cell")

    def _create_data_transformation_widget(self, cell_type):
        ''' Creates a data transformation section for a given cell type'''
        # Initialize UI vars for cell_type
        self._intialize_UI_vars(cell_type)

        self.data_transformation_widget_frame = tk.LabelFrame(self.data_transformation_sections_frame, text=cell_type, font=UIStyling.LABEL_FONT)
        self.data_transformation_widget_frame.pack(side="left", fill="x", padx=UIStyling.PAD_X, pady=UIStyling.PAD_Y)

        # Create subsections
        self._create_load_data_sub_widget(cell_type)
        self._create_filter_data_sub_widget(cell_type)
        self._create_extract_data_sub_widget(cell_type)
        self._create_modify_data_sub_widget(cell_type)
        self._create_fit_data_sub_widget(cell_type)
        self._create_visualize_data_sub_widget(cell_type)
        self._create_plot_data_sub_widget(cell_type)
        self._create_data_processing_sub_widget(cell_type)
                
    def _intialize_UI_vars(self, cell_type):
        ''' Initialize UI vars for cell type'''
        # filter widget vars
        # boolean vars
        boolean_vars = {
            "apply_range_filter": False,
            "remove_pause": False,
            "select_cycle": False,
            "select_charge_half_cycle": False,
            "select_discharge_half_cycle": False,
            "apply_step_change": False,
        }
        for var, default_value in boolean_vars.items():
            if cell_type not in getattr(self, var):
                getattr(self, var)[cell_type] = tk.BooleanVar(value=default_value)  # ✅ Set default value

        # filter_data_widget - dropdowns
        self.selected_cycle[cell_type] = tk.StringVar(value="All")
        self.selected_cycle_column[cell_type] = tk.StringVar(value="Cyc-Count")
        self.selected_step_change_column[cell_type] = tk.StringVar(value="Line")

        # fit widget vars
        self.fit_option[cell_type] = tk.StringVar(value="no fit")
        self.use_step_size[cell_type] = tk.BooleanVar(value=False)
        self.use_step_size[cell_type] = tk.BooleanVar(value=False)

        # plot widget vars
        self.plot_option[cell_type] = tk.StringVar(value="U-t")

        # modify_data_widget vars
        self.selected_column[cell_type] = tk.StringVar()
        self.offset_value[cell_type] = tk.DoubleVar()
        self.compute_du_dq[cell_type] = tk.BooleanVar()
        self.compute_abs_cycle[cell_type] = tk.BooleanVar()
        self.normalize_voltage[cell_type] = tk.BooleanVar()
        self.apply_offset[cell_type] = tk.BooleanVar()

        # visualize_data_widget vars
        self.visualize_key_values[cell_type] = tk.BooleanVar(value=False)
        self.show_cycles = tk.BooleanVar(value=False)
        # data_processing_widget - dropdown
        self.selected_data_type = tk.StringVar(value="Modified Data")

    def _create_load_data_sub_widget(self, cell_type):
        '''Creates UI Elements of load_data sub widget of the data transformation section'''
        load_data_sub_widget_frame = UIElements.section_frame(self.data_transformation_widget_frame, "load data")    
        load_label_frame=UIElements.frame(load_data_sub_widget_frame)
        UIElements.label(load_label_frame, text=f"{cell_type} file:")
        UIElements.label(load_label_frame, text= "No file selected") #change --> parameter

        load_buttons_frame=UIElements.frame(load_data_sub_widget_frame)
        UIElements.button(load_buttons_frame, "Load", command=lambda: self._load_file) #change
        UIElements.button(load_buttons_frame, "Show Data Table", command=lambda: self._show_data_table) #change
        UIElements.button(load_buttons_frame, "Plot Data", command=lambda: self._plot_data) #change

    def _create_filter_data_sub_widget(self, cell_type):
        '''Creates UI Elements of filter_data subsetion of the data transformation section'''
        
        filter_data_sub_widget_frame = UIElements.section_frame(self.data_transformation_widget_frame, "filter data")
        # create checkbuttons for simple filters
        checkbuttons = [
            ("Remove pause", self.remove_pause[cell_type]),
            ("Select charge half cycle", self.select_charge_half_cycle[cell_type]),
            ("Select discharge half cycle", self.select_discharge_half_cycle[cell_type]),
        ]
        for label, var in checkbuttons:
            UIElements.checkbutton(filter_data_sub_widget_frame, label, variable=var)

        # create checkbuttons for filters with additional UI elements
        UIElements.checkbutton(filter_data_sub_widget_frame, "Apply range filter",
                        variable=self.apply_range_filter[cell_type])
        
        self.cycle_filter_frame = UIElements.frame(filter_data_sub_widget_frame)
        UIElements.checkbutton(self.cycle_filter_frame, "Select cycle",
                               variable=self.select_cycle[cell_type])
        # cycle_dropdown
        self.cycle_dropdown = tk.OptionMenu(self.cycle_filter_frame, self.selected_cycle, "")
        self.cycle_dropdown.config(font=UIStyling.DROPDOWN_FONT, state="disabled")
        self.cycle_dropdown.pack(side="left", padx=UIStyling.DROPDOWN_PADX)
        # cycle_column dropdown
        self.cycle_column_dropdown = tk.OptionMenu(self.cycle_filter_frame, self.selected_cycle_column, "Cyc-Count", "abs_cycle", command=lambda:self._update_cycle_column_dropdown) #change command 
        self.cycle_column_dropdown.config(font=UIStyling.DROPDOWN_FONT, state="disabled")      
        self.cycle_column_dropdown.pack(side="left", padx=UIStyling.DROPDOWN_PADX)

        self.step_change_filter_frame = UIElements.frame(filter_data_sub_widget_frame)
        UIElements.checkbutton(self.step_change_filter_frame, text="Apply step change filter",
                variable=self.apply_step_change[cell_type])
        self.step_change_dropdown = tk.OptionMenu(self.step_change_filter_frame, self.selected_step_change_column, "Line", "Command", "Cyc-Count")
        self.step_change_dropdown.config(font=UIStyling.DROPDOWN_FONT)  # ✅ Apply centralized font
        self.step_change_dropdown.pack(side="left", padx=UIStyling.DROPDOWN_PADX)

    def _create_extract_data_sub_widget(self, cell_type):
        '''Creates UI elements of extract_data sub widget of the data transformation section'''
        extract_data_sub_widget_frame = UIElements.section_frame(self.data_transformation_widget_frame, "extract data")    
        
    def _create_modify_data_sub_widget(self, cell_type):
        '''Creates UI elements of modify_data sub widget of the data transformation section'''
        modify_data_sub_widget_frame = UIElements.section_frame(self.data_transformation_widget_frame, "modify data")    
     
        tk.Checkbutton(modify_data_sub_widget_frame, text="Compute dU/dQ", variable=self.compute_du_dq, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)
        tk.Checkbutton(modify_data_sub_widget_frame, text="Compute Absolute Cycle", variable=self.compute_abs_cycle, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)
        tk.Checkbutton(modify_data_sub_widget_frame, text="Normalize Voltage", variable=self.normalize_voltage, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)
        
        # Offset UI Elements
        offset_frame = tk.Frame(modify_data_sub_widget_frame)
        offset_frame.pack(fill="x", pady=UIStyling.PAD_Y)
        tk.Checkbutton(offset_frame, text="Apply Offset", variable=self.apply_offset, font=UIStyling.CHECKBOX_FONT, command=lambda: self.toggle_offset_controls).pack(side="left")

        self.column_dropdown = tk.OptionMenu(offset_frame, self.selected_column, "Select Column")
        self.column_dropdown.config(font=UIStyling.DROPDOWN_FONT, state="disabled")  # ✅ Apply centralized font
        self.column_dropdown.pack(side="left", fill="x", expand=True, padx=UIStyling.DROPDOWN_PADX)
        
        self.offset_entry = tk.Entry(offset_frame, textvariable=self.offset_value, font=UIStyling.ENTRY_FONT, width=10)
        self.offset_entry.pack(side="left", padx=UIStyling.PAD_X)

    def _create_fit_data_sub_widget(self, cell_type):
        '''Creates UI elements of fit_data sub widget of the data transformation section'''
        fit_data_sub_widget_frame = UIElements.section_frame(self.data_transformation_widget_frame, "fit data")    
        tk.Radiobutton(fit_data_sub_widget_frame, text="No Fit", variable=self.fit_option, value="no fit",
                       font=UIStyling.BUTTON_FONT, command=lambda: self._toggle_use_step_size_checkbox).pack(anchor="w", padx=UIStyling.LISTBOX_PADX)
        

        linear_spline_frame = tk.Frame(fit_data_sub_widget_frame)
        linear_spline_frame.pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)

        tk.Radiobutton(linear_spline_frame, text="Linear Spline", variable=self.fit_option, value="linear spline",
                       font=UIStyling.BUTTON_FONT, command=lambda: self._toggle_use_step_size_checkbox).pack(side="left", anchor="w", padx=UIStyling.LISTBOX_PADX)

        # "Use Step Size" Checkbox
        self.step_size_checkbox = tk.Checkbutton(linear_spline_frame, text="Use Step Size", variable=self.use_step_size,
                                                 font=UIStyling.BUTTON_FONT, state="disabled",
                                                 command=lambda: self._toggle_step_size_entryfield)
        self.step_size_checkbox.pack(side="left", anchor="w", padx=UIStyling.LISTBOX_PADX)

        # Step Size Entry Field
        self.step_size_entry = tk.Entry(linear_spline_frame, textvariable=self.step_size_value,
                                        font=UIStyling.ENTRY_FONT, width=10, state="disabled")
        self.step_size_entry.pack(side="left", anchor="w", padx=UIStyling.LISTBOX_PADX)

    def _create_visualize_data_sub_widget(self, cell_type):
        '''Creates UI elements of visualize_data sub widget of the data transformation section'''
        visualize_data_sub_widget_frame = UIElements.section_frame(self.data_transformation_widget_frame, "visualize data")    
        
        visualization_frame = tk.LabelFrame(visualize_data_sub_widget_frame, text="Select visualization type", font=UIStyling.LABEL_FONT)
        visualization_frame.pack(fill="both", expand=True, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)
        tk.Checkbutton(visualization_frame, text="Show Key Values", variable=self.visualize_key_values, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)
        tk.Checkbutton(visualization_frame, text="Show Cycles", variable=self.show_cycles, font=UIStyling.BUTTON_FONT).pack(side="left", padx=5)

    def _create_plot_data_sub_widget(self, cell_type):
        '''Creates UI elements of plot_data sub widget of the data transformation section'''
        plot_data_sub_widget_frame = UIElements.section_frame(self.data_transformation_widget_frame, "plot data")    

        tk.Radiobutton(plot_data_sub_widget_frame, text="U vs t (Voltage-Time)", variable=self.plot_option, value="U-t", font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX)
        tk.Radiobutton(plot_data_sub_widget_frame, text="I vs t (Current-Time)", variable=self.plot_option, value="I-t", font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX)
        tk.Radiobutton(plot_data_sub_widget_frame, text="Q vs U (Charge-Voltage)", variable=self.plot_option, value="Q-U", font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX)

    def _create_data_processing_sub_widget(self, cell_type):
        '''Creates UI elements of plot_data sub widget of the data transformation section'''
        data_interaction_sub_widget_frame = UIElements.section_frame(self.data_transformation_widget_frame, "plot data")    

        tk.Button(data_interaction_sub_widget_frame, text="Plot Filtered Data", command=lambda: self._plot_filtered_data, font=UIStyling.BUTTON_FONT).pack(side="left", padx=5)
        tk.Button(data_interaction_sub_widget_frame, text="Save Filtered Data", command=lambda: self._save_filtered_data, font=UIStyling.BUTTON_FONT).pack(side="left", padx=5)
        tk.Button(data_interaction_sub_widget_frame, text="Store Filtered Data", command=lambda: self._store_filtered_data, font=UIStyling.BUTTON_FONT).pack(side="left", padx=5)


        self.data_type_dropdown = tk.OptionMenu(data_interaction_sub_widget_frame, self.selected_data_type, "Modified Data", "Fit Data")
        self.data_type_dropdown.config(font=UIStyling.DROPDOWN_FONT, state="disabled")
        self.data_type_dropdown.pack(side="left", padx=5)

