### data_handling.py

import tkinter as tk
from tkinter import messagebox
from styles import UIStyling

class ModifyDataWidget:
    """
    A widget for modifying datasets with additional computed columns.
    """
    def __init__(self, parent, label_text, dataset_type, app_context):
        self.app_context = app_context
        self.dataset_type = dataset_type

        self.frame = tk.LabelFrame(parent, text=label_text, font=UIStyling.LABEL_FONT)
        self.frame.pack(side="left", fill="both", expand=True, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        self.compute_du_dq = tk.BooleanVar()
        self.compute_abs_cycle = tk.BooleanVar()
        self.normalize_voltage = tk.BooleanVar()
        self.apply_offset = tk.BooleanVar()

        # Modification options
        tk.Checkbutton(self.frame, text="Compute dU/dQ", variable=self.compute_du_dq, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)
        tk.Checkbutton(self.frame, text="Compute Absolute Cycle", variable=self.compute_abs_cycle, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)
        tk.Checkbutton(self.frame, text="Normalize Voltage", variable=self.normalize_voltage, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)

        '''
        # Apply Offset Checkbutton
        self.apply_offset = tk.BooleanVar()
        tk.Checkbutton(self.frame, text="Apply Offset", variable=self.apply_offset, command=self.toggle_offset_controls).pack(anchor="w")

        # Column Selection for Offset (Dropdown)
        self.selected_column = tk.StringVar()
        self.selected_column.set("Select Column")
        self.column_dropdown = tk.OptionMenu(self.frame, self.selected_column, "Select Column")
        self.column_dropdown.pack(fill="x", pady=UIStyling.PAD_Y)
        self.column_dropdown.config(state="disabled")  # Initially disabled

        # Offset Value Entry
        self.offset_value = tk.DoubleVar()
        self.offset_entry = tk.Entry(self.frame, textvariable=self.offset_value)
        self.offset_entry.pack(fill="x", pady=UIStyling.PAD_Y)
        self.offset_entry.insert(0, "0")
        self.offset_entry.config(state="disabled")  # Initially disabled
        
        '''
        # Offset UI Elements
        offset_frame = tk.Frame(self.frame)
        offset_frame.pack(fill="x", pady=UIStyling.PAD_Y)

        tk.Checkbutton(offset_frame, text="Apply Offset", variable=self.apply_offset, font=UIStyling.CHECKBOX_FONT, command=self.toggle_offset_controls).pack(side="left")

        self.selected_column = tk.StringVar()
        self.column_dropdown = tk.OptionMenu(offset_frame, self.selected_column, "Select Column")
        self.column_dropdown.config(font=UIStyling.DROPDOWN_FONT, state="disabled")  # ✅ Apply centralized font
        self.column_dropdown.pack(side="left", fill="x", expand=True, padx=UIStyling.DROPDOWN_PADX)
        self.offset_value = tk.DoubleVar()
        self.offset_entry = tk.Entry(offset_frame, textvariable=self.offset_value, font=UIStyling.ENTRY_FONT, width=10)
        self.offset_entry.pack(side="left", padx=UIStyling.PAD_X)
    
    def toggle_offset_controls(self):
        """ Enable/Disable column selection and offset value input based on checkbutton state. """
        if self.apply_offset.get():
            self.column_dropdown.config(state="normal")
            self.offset_entry.config(state="normal")
        else:
            self.column_dropdown.config(state="disabled")
            self.offset_entry.config(state="disabled")

    '''
        def update_column_dropdown(self, column_names):
        """
        Updates the dropdown with available column names.
        """
        self.column_dropdown["menu"].delete(0, "end")  # Clear previous entries
        for col in column_names:
            self.column_dropdown["menu"].add_command(label=col, command=lambda value=col: self.selected_column.set(value))
        if column_names:
            self.selected_column.set(column_names[0])  # Default to first column
    
    '''

    def update_column_dropdown(self, column_names):
        """
        Updates the dropdown with available column names.
        """
        self.column_dropdown["menu"].delete(0, "end")  # Clear previous entries
        for col in column_names:
            self.column_dropdown["menu"].add_command(label=col, command=tk._setit(self.selected_column, col))
        if column_names:
            self.selected_column.set(column_names[0])  # Default to first column

    def update_column_dropdown(self, column_names):
        """
        Updates the dropdown with available column names.
        """
        self.column_dropdown["menu"].delete(0, "end")  # Clear previous entries
        for col in column_names:
            self.column_dropdown["menu"].add_command(label=col, command=lambda value=col: self.selected_column.set(value))
        if column_names:
            self.selected_column.set(column_names[0])  # Default to first column

    def update_column_options(self, dataset):
            """ Update the dropdown menu with available column names from the dataset. """
            if dataset is not None:
                columns = dataset.columns.tolist()
                self.column_dropdown["menu"].delete(0, "end")
                for col in columns:
                    self.column_dropdown["menu"].add_command(label=col, command=lambda value=col: self.selected_column.set(value))

'''
    def update_modify_widgets(self, dataset_type):
        """
        Updates the ModifyDataWidget dropdown with available column names from the dataset.
        """
        dataset = self.datasets.get(dataset_type, {}).get("data")
        widget = self.app.anode_modify_widget if dataset_type == "anode" else self.app.cathode_modify_widget

        if dataset is not None:
            column_names = dataset.columns.tolist()
            widget.update_column_dropdown(column_names)
        else:
            widget.update_column_dropdown([])  # Clear dropdown if no dataset is loaded

'''

class FilterWidget:
    """
    Widget for handling filter options and visualization types.
    """

    def __init__(self, parent, label_text, dataset_type, app_context):
        self.app_context = app_context
        self.dataset_type = dataset_type

        self.frame = tk.LabelFrame(parent, text=label_text, font=UIStyling.LABEL_FONT)
        self.frame.pack(fill="both", expand=True, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        self.remove_pause = tk.BooleanVar()
        self.select_cycle = tk.BooleanVar()
        self.select_charge_half_cycle = tk.BooleanVar()
        self.select_discharge_half_cycle = tk.BooleanVar()
        self.apply_step_change = tk.BooleanVar()
        self.step_change_column = tk.StringVar(value="Line")  
        self.plot_option = tk.StringVar(value="U-t")
        self.fit_option = tk.StringVar(value="no fit")
        self.visualize_key_values = tk.BooleanVar(value=False)
        self.show_cycles = tk.BooleanVar(value=False)
        self.cycle_selection = tk.StringVar(value="All")
        self.cycle_column_option = tk.StringVar(value="Cyc-Count")  

        # ✅ Ensure Range Filter UI is separate from other elements
        range_filter_frame = tk.LabelFrame(self.frame, text="Filter by Range", font=UIStyling.LABEL_FONT)
        range_filter_frame.pack(fill="x", padx=10, pady=5)

        self.apply_range_filter = tk.BooleanVar(value=False)
        self.range_filter_checkbox = tk.Checkbutton(
            range_filter_frame, text="Apply Range Filter", variable=self.apply_range_filter, command=self.toggle_range_controls
        )
        self.range_filter_checkbox.pack(anchor="w")

        self.selected_column = tk.StringVar()
        self.column_dropdown = tk.OptionMenu(range_filter_frame, self.selected_column, "Select Column")
        self.column_dropdown.config(font=UIStyling.DROPDOWN_FONT, state="disabled")
        self.column_dropdown.pack(fill="x", padx=UIStyling.DROPDOWN_PADX)

        range_values_frame = tk.Frame(range_filter_frame)
        range_values_frame.pack(fill="x")

        tk.Label(range_values_frame, text="Min:", font=UIStyling.LABEL_FONT).pack(side="left")
        self.min_value = tk.DoubleVar()
        self.min_entry = tk.Entry(range_values_frame, textvariable=self.min_value, font=UIStyling.ENTRY_FONT, state="disabled", width=10)
        self.min_entry.pack(side="left", padx=5)

        tk.Label(range_values_frame, text="Max:", font=UIStyling.LABEL_FONT).pack(side="left")
        self.max_value = tk.DoubleVar()
        self.max_entry = tk.Entry(range_values_frame, textvariable=self.max_value, font=UIStyling.ENTRY_FONT, state="disabled", width=10)
        self.max_entry.pack(side="left", padx=5)

        # ✅ Create filter options after adding range UI
        self._create_filter_options()

        # ✅ Ensure buttons are added at the bottom
        self._add_action_buttons()


    def _add_action_buttons(self):
        """Ensures buttons are added correctly at the bottom."""
        button_frame = tk.Frame(self.frame)
        button_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(button_frame, text="Plot Filtered Data", command=self._plot_filtered_data, font=UIStyling.BUTTON_FONT).pack(side="left", padx=5)
        tk.Button(button_frame, text="Save Filtered Data", command=self._save_filtered_data, font=UIStyling.BUTTON_FONT).pack(side="left", padx=5)
        tk.Button(button_frame, text="Store Filtered Data", command=self._store_filtered_data, font=UIStyling.BUTTON_FONT).pack(side="left", padx=5)

    def toggle_range_controls(self):
        """ Enable/Disable range filter controls based on checkbox state. """
        state = "normal" if self.apply_range_filter.get() else "disabled"
        self.column_dropdown.config(state=state)
        self.min_entry.config(state=state)
        self.max_entry.config(state=state)

    def update_column_dropdown(self, column_names):
        """ Updates the dropdown with available column names. """
        self.column_dropdown["menu"].delete(0, "end")  
        for col in column_names:
            self.column_dropdown["menu"].add_command(label=col, command=tk._setit(self.selected_column, col))
        if column_names:
            self.selected_column.set(column_names[0])

        self._create_filter_options()

      #  # Add Plot and Save Buttons
      #  tk.Button(self.frame, text="Plot Filtered Data", command=self._plot_filtered_data, font=UIStyling.BUTTON_FONT).grid(row=1, column=0, padx=10, pady=5, sticky="w")
      #  tk.Button(self.frame, text="Save Filtered Data", command=self._save_filtered_data, font=UIStyling.BUTTON_FONT).grid(row=1, column=1, padx=10, pady=5, sticky="w")
      #  tk.Button(self.frame, text="Store Filtered Data", command=self._store_filtered_data, font=UIStyling.BUTTON_FONT).grid(row=1, column=2, padx=10, pady=5, sticky="w")

        # Add Plot and Save Buttons
        tk.Button(self.frame, text="Plot Filtered Data", command=self._plot_filtered_data, font=UIStyling.BUTTON_FONT).pack(side="left", padx=10, pady=5)
        tk.Button(self.frame, text="Save Filtered Data", command=self._save_filtered_data, font=UIStyling.BUTTON_FONT).pack(side="left", padx=10, pady=5)
        tk.Button(self.frame, text="Store Filtered Data", command=self._store_filtered_data, font=UIStyling.BUTTON_FONT).pack(side="left", padx=10, pady=5)

    def _create_filter_options(self):
        """ Creates filter selection UI while preserving previously created UI elements. """
        if hasattr(self, "filter_frame"):
            # Prevent duplicate UI from being created
            return

        # Filter Criteria
        self.filter_frame = tk.LabelFrame(self.frame, text="Select filter criteria", font=UIStyling.LABEL_FONT)
        self.filter_frame.pack(fill="both", expand=True, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        tk.Checkbutton(self.filter_frame, text="Remove pause", variable=self.remove_pause, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)

        # Select Cycle with Dropdown
        cycle_frame = tk.Frame(self.filter_frame)
        cycle_frame.pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)
        tk.Checkbutton(cycle_frame, text="Select cycle", variable=self.select_cycle, command=self._toggle_cycle_dropdown, font=UIStyling.BUTTON_FONT).pack(side="left")
        self.cycle_dropdown = tk.OptionMenu(cycle_frame, self.cycle_selection, "")
        self.cycle_dropdown.config(font=UIStyling.DROPDOWN_FONT, state="disabled")
        self.cycle_dropdown.pack(side="left", padx=UIStyling.DROPDOWN_PADX)

        tk.Checkbutton(self.filter_frame, text="Select charge half cycle", variable=self.select_charge_half_cycle, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)
        tk.Checkbutton(self.filter_frame, text="Select discharge half cycle", variable=self.select_discharge_half_cycle, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)

        # Step Change Filter UI
        step_change_frame = tk.Frame(self.filter_frame)
        step_change_frame.pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)

        tk.Checkbutton(step_change_frame, text="Apply Step Change Filter", variable=self.apply_step_change, font=UIStyling.BUTTON_FONT).pack(side="left")
        self.step_change_dropdown = tk.OptionMenu(step_change_frame, self.step_change_column, "Line", "Command", "Cyc-Count")
        self.step_change_dropdown.config(font=UIStyling.DROPDOWN_FONT)  # ✅ Apply centralized font
        self.step_change_dropdown.pack(side="left", padx=UIStyling.DROPDOWN_PADX)

        # Plot Type Selection
        plot_frame = tk.LabelFrame(self.frame, text="Select plot type", font=UIStyling.LABEL_FONT)
        # plot_frame.grid(row=0, column=1, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY, sticky="nsew")
        plot_frame.pack(fill="both", expand=True, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        tk.Radiobutton(plot_frame, text="U vs t (Voltage-Time)", variable=self.plot_option, value="U-t", font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX)
        tk.Radiobutton(plot_frame, text="I vs t (Current-Time)", variable=self.plot_option, value="I-t", font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX)
        tk.Radiobutton(plot_frame, text="Q vs U (Charge-Voltage)", variable=self.plot_option, value="Q-U", font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX)

        # Fit Type Selection
        fit_frame = tk.LabelFrame(self.frame, text="Select fit type", font=UIStyling.LABEL_FONT)
        # fit_frame.grid(row=0, column=2, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY, sticky="nsew")
        fit_frame.pack(fill="both", expand=True, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        tk.Radiobutton(fit_frame, text="No Fit", variable=self.fit_option, value="no fit", font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX)
        tk.Radiobutton(fit_frame, text="Linear Spline", variable=self.fit_option, value="linear spline", font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX)

        # Visualization Options
        visualization_frame = tk.LabelFrame(self.frame, text="Select visualization type", font=UIStyling.LABEL_FONT)
        # visualization_frame.grid(row=0, column=3, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY, sticky="nsew")
        visualization_frame.pack(fill="both", expand=True, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        # Show Key Values Checkbox (Keep it separate)
        tk.Checkbutton(visualization_frame, text="Show Key Values", variable=self.visualize_key_values, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)

        # Frame for Show Cycles and Dropdown (Ensures Side-by-Side Layout)
        cycles_frame = tk.Frame(visualization_frame)
        cycles_frame.pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2, fill="x")

        tk.Checkbutton(cycles_frame, text="Show Cycles", variable=self.show_cycles, font=UIStyling.BUTTON_FONT).pack(side="left", padx=5)
        self.cycle_column_dropdown = tk.OptionMenu(cycles_frame, self.cycle_column_option, "Cyc-Count", "abs_cycle")
        self.cycle_column_dropdown.config(font=UIStyling.DROPDOWN_FONT)
        self.cycle_column_dropdown.pack(side="left", padx=UIStyling.DROPDOWN_PADX)

    def _toggle_cycle_dropdown(self):
        """
        Enable or disable the cycle dropdown based on the Select Cycle checkbox.
        """
        if self.select_cycle.get():
            self.cycle_dropdown.config(state="normal")
        else:
            self.cycle_dropdown.config(state="disabled")

    def _plot_filtered_data(self):
        """
        Plot the filtered data for the dataset.
        """
        if hasattr(self.app_context, "plot_filtered_data"):
            self.app_context.plot_filtered_data(self.dataset_type)
        else:
            messagebox.showerror("Error", "Plotting functionality is not available.")

    def _save_filtered_data(self):
        """
        Save the filtered dataset to a file.
        """
        if hasattr(self.app_context, "save_filtered_data"):
            self.app_context.save_filtered_data(self.dataset_type)
        else:
            messagebox.showerror("Error", "Save functionality is not available.")

    def _store_filtered_data(self):
        """
        Store the filtered dataset for further use.
        """
        if hasattr(self.app_context, "store_filtered_data"):
            self.app_context.store_filtered_data(self.dataset_type)
        else:
            messagebox.showerror("Error", "Store functionality is not available.")

    def update_cycle_options(self, cycles):
        """
        Updates the cycle dropdown options based on the dataset.
        """
        menu = self.cycle_dropdown["menu"]
        menu.delete(0, "end")  # Clear existing options
        menu.add_command(label="All", command=lambda: self.cycle_selection.set("All"))  # Add "All" option
        for cycle in sorted(cycles):
            menu.add_command(label=str(cycle), command=lambda c=cycle: self.cycle_selection.set(str(c)))

class KeyValuesWidget:
    """
    Widget for handling the extraction of key values for anode/cathode datasets.
    """
    def __init__(self, parent, label_text, dataset_type, app_context):
        self.app_context = app_context
        self.dataset_type = dataset_type

        self.frame = tk.LabelFrame(
            parent, text=label_text, font=UIStyling.LABEL_FONT
        )
        self.frame.pack(  # ✅ FIXED: Changed from grid() to pack()
            fill="both", expand=True, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY
        )

        self.extract_max_voltage = tk.BooleanVar()
        self.extract_max_charge = tk.BooleanVar()
        self.extract_max_discharge = tk.BooleanVar()

        # Key Value Checkboxes
        tk.Checkbutton(
            self.frame, text="Max Voltage", variable=self.extract_max_voltage, 
            font=UIStyling.BUTTON_FONT
        ).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)

        tk.Checkbutton(
            self.frame, text="Max Ah-Cyc-Charge-0", variable=self.extract_max_charge, 
            font=UIStyling.BUTTON_FONT
        ).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)

        tk.Checkbutton(
            self.frame, text="Max Ah-Cyc-Discharge-0", variable=self.extract_max_discharge, 
            font=UIStyling.BUTTON_FONT
        ).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)

        # Extract Button
        tk.Button(
            self.frame, text="Extract Key Values", 
            command=self._extract_key_values, font=UIStyling.BUTTON_FONT
        ).pack(pady=UIStyling.FRAME_PADY)

    def _extract_key_values(self):
        """
        Extract key values for the dataset.
        """
        self.app_context.extract_key_values(self.dataset_type)
