import tkinter as tk
from tkinter import messagebox
from styles import UIStyling

### widget for data import section

class DataWidget:
    """
    Widget for handling file operations and plotting for anode/cathode datasets.
    """
    def __init__(self, parent, label_text, dataset_key, data_manager):
        self.data_manager = data_manager  # ✅ Now it stores a reference to DataManager
        self.dataset_key = dataset_key

        self.frame = tk.Frame(parent, relief="groove", borderwidth=2)
        self.frame.pack(side="left", fill="both", expand=True, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        # File Operations
        label_frame = tk.Frame(self.frame)
        label_frame.pack(fill="x", pady=2)

        tk.Label(label_frame, text=f"{label_text} file:", font=UIStyling.LABEL_FONT).pack(side="left", padx=5)

        # ✅ Use data_manager instead of app_context
        self.file_label = tk.Label(label_frame, textvariable=self.data_manager.datasets[dataset_key]["file_path"], width=40, anchor="w")
        self.file_label.pack(side="left", fill="x", expand=True, padx=5)

        # Buttons Frame
        button_frame = tk.Frame(self.frame)
        button_frame.pack(fill="x", pady=2)

        tk.Button(button_frame, text="Load", command=self._load_file, font=UIStyling.BUTTON_FONT).pack(side="left", padx=5, pady=2)
        tk.Button(button_frame, text="Show Data Table", command=self._show_data_table, font=UIStyling.BUTTON_FONT).pack(side="left", padx=5, pady=2)
        tk.Button(button_frame, text="Plot Data", command=self._plot_data, font=UIStyling.BUTTON_FONT).pack(side="left", padx=5, pady=2)

    def _load_file(self):
        self.data_manager.select_file(self.dataset_key)  # ✅ Call DataManager

    def _show_data_table(self):
        self.data_manager.show_data_table(self.dataset_key)  # ✅ Call DataManager

    def _plot_data(self):
        self.data_manager.plot_data(self.dataset_key)  # ✅ Call DataManager

# widgets for data modification section 

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
        self.use_step_size = tk.BooleanVar(value=False)  # New BooleanVar for step size checkbox
        self.step_size_value = tk.DoubleVar(value=0.01)  # Default step size
        self.visualize_key_values = tk.BooleanVar(value=False)
        self.show_cycles = tk.BooleanVar(value=False)
        self.cycle_selection = tk.StringVar(value="All")
        self.cycle_column = tk.StringVar(value="Cyc-Count")
        self.apply_range_filter = tk.BooleanVar(value=False)

        # Create filter options section
        self._create_filter_options()

        # frame for action buttons and data_type_dropdown
        self.button_frame = tk.Frame(self.frame)
        self.button_frame.pack(fill="x", padx=10, pady=5)
        self._add_action_buttons()
        self._add_data_type_dropdown()

    def _create_filter_options(self):
        """ Creates filter selection UI while preserving previously created UI elements. """
        if hasattr(self, "filter_frame"):
            # Prevent duplicate UI from being created
            return

        # Filter Criteria
        self.filter_frame = tk.LabelFrame(self.frame, text="Select filter criteria", font=UIStyling.LABEL_FONT)
        self.filter_frame.pack(fill="both", expand=True, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        # Row for Apply Range Filter
        range_frame = tk.Frame(self.filter_frame)
        range_frame.pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)
        tk.Checkbutton(range_frame, text="Apply Range Filter", variable=self.apply_range_filter, command=self.toggle_range_controls, font=UIStyling.BUTTON_FONT).pack(side="left")
        self.selected_column = tk.StringVar()
        self.column_dropdown = tk.OptionMenu(range_frame, self.selected_column, "Select Column")
        self.column_dropdown.config(font=UIStyling.DROPDOWN_FONT, state="disabled")
        self.column_dropdown.pack(side="left", padx=UIStyling.DROPDOWN_PADX)
        tk.Label(range_frame, text="Min:", font=UIStyling.BUTTON_FONT).pack(side="left", padx=5)
        self.min_value = tk.DoubleVar()
        self.min_entry = tk.Entry(range_frame, textvariable=self.min_value, font=UIStyling.ENTRY_FONT, state="disabled", width=10)
        self.min_entry.pack(side="left", padx=5)
        tk.Label(range_frame, text="Max:", font=UIStyling.BUTTON_FONT).pack(side="left", padx=5)
        self.max_value = tk.DoubleVar()
        self.max_entry = tk.Entry(range_frame, textvariable=self.max_value, font=UIStyling.ENTRY_FONT, state="disabled", width=10)
        self.max_entry.pack(side="left", padx=5)

        tk.Checkbutton(self.filter_frame, text="Remove pause", variable=self.remove_pause, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)

        # Select Cycle UI
        cycle_frame = tk.Frame(self.filter_frame)
        cycle_frame.pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)
        tk.Checkbutton(cycle_frame, text="Select cycle", variable=self.select_cycle, command=self._toggle_cycle_dropdowns, font=UIStyling.BUTTON_FONT).pack(side="left")   
        # Dropdown for selection the cycle
        self.cycle_dropdown = tk.OptionMenu(cycle_frame, self.cycle_selection, "")
        self.cycle_dropdown.config(font=UIStyling.DROPDOWN_FONT, state="disabled")
        self.cycle_dropdown.pack(side="left", padx=UIStyling.DROPDOWN_PADX)
        # Dropdown for selecting the cycle column type (Cyc-Count or abs_cycle)
        self.cycle_column = tk.StringVar(value="Cyc-Count")
        self.cycle_column_dropdown = tk.OptionMenu(
            cycle_frame, self.cycle_column, "Cyc-Count", "abs_cycle", command=self._update_cycle_column_dropdown
        )
#        self.cycle_column_dropdown.config(font=UIStyling.DROPDOWN_FONT)
        self.cycle_column_dropdown.config(font=UIStyling.DROPDOWN_FONT, state="disabled") # hkw
    #    self.cycle_column_dropdown.config(font=UIStyling.DROPDOWN_FONT, state="normal")  # Default to enabled        
        self.cycle_column_dropdown.pack(side="left", padx=UIStyling.DROPDOWN_PADX)

        # Charge and Discharge Halfcycle UI
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
        plot_frame.pack(fill="both", expand=True, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)
        tk.Radiobutton(plot_frame, text="U vs t (Voltage-Time)", variable=self.plot_option, value="U-t", font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX)
        tk.Radiobutton(plot_frame, text="I vs t (Current-Time)", variable=self.plot_option, value="I-t", font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX)
        tk.Radiobutton(plot_frame, text="Q vs U (Charge-Voltage)", variable=self.plot_option, value="Q-U", font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX)

        # Fit Type Selection
        fit_frame = tk.LabelFrame(self.frame, text="Select fit type", font=UIStyling.LABEL_FONT)
        fit_frame.pack(fill="both", expand=True, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)
        tk.Radiobutton(fit_frame, text="No Fit", variable=self.fit_option, value="no fit",
                       font=UIStyling.BUTTON_FONT, command=self._toggle_use_step_size_checkbox).pack(anchor="w", padx=UIStyling.LISTBOX_PADX)
        

        linear_spline_frame = tk.Frame(fit_frame)
        linear_spline_frame.pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)

        tk.Radiobutton(linear_spline_frame, text="Linear Spline", variable=self.fit_option, value="linear spline",
                       font=UIStyling.BUTTON_FONT, command=self._toggle_use_step_size_checkbox).pack(side="left", anchor="w", padx=UIStyling.LISTBOX_PADX)

        # "Use Step Size" Checkbox
        self.step_size_checkbox = tk.Checkbutton(linear_spline_frame, text="Use Step Size", variable=self.use_step_size,
                                                 font=UIStyling.BUTTON_FONT, state="disabled",
                                                 command=self._toggle_step_size_entryfield)
        self.step_size_checkbox.pack(side="left", anchor="w", padx=UIStyling.LISTBOX_PADX)

        # Step Size Entry Field
        self.step_size_entry = tk.Entry(linear_spline_frame, textvariable=self.step_size_value,
                                        font=UIStyling.ENTRY_FONT, width=10, state="disabled")
        self.step_size_entry.pack(side="left", anchor="w", padx=UIStyling.LISTBOX_PADX)

        # Visualization Selection
        visualization_frame = tk.LabelFrame(self.frame, text="Select visualization type", font=UIStyling.LABEL_FONT)
        visualization_frame.pack(fill="both", expand=True, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)
        tk.Checkbutton(visualization_frame, text="Show Key Values", variable=self.visualize_key_values, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)
        tk.Checkbutton(visualization_frame, text="Show Cycles", variable=self.show_cycles, font=UIStyling.BUTTON_FONT).pack(side="left", padx=5)

    def _add_action_buttons(self):
        """Ensures buttons are added correctly at the bottom."""
#        button_frame = tk.Frame(self.frame)
#        button_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(self.button_frame, text="Plot Filtered Data", command=self._plot_filtered_data, font=UIStyling.BUTTON_FONT).pack(side="left", padx=5)
        tk.Button(self.button_frame, text="Save Filtered Data", command=self._save_filtered_data, font=UIStyling.BUTTON_FONT).pack(side="left", padx=5)
        tk.Button(self.button_frame, text="Store Filtered Data", command=self._store_filtered_data, font=UIStyling.BUTTON_FONT).pack(side="left", padx=5)

    def _add_data_type_dropdown(self):
        """Dropdown to select modified or fit data to save or store using tk.buttons"""
        # ✅ Add Data Type Dropdown (Disabled initially)
        self.data_type_selection = tk.StringVar(value="Modified Data")
        self.data_type_dropdown = tk.OptionMenu(self.button_frame, self.data_type_selection, "Modified Data", "Fit Data")
        self.data_type_dropdown.config(font=UIStyling.DROPDOWN_FONT, state="disabled")
        self.data_type_dropdown.pack(side="left", padx=5)

        # ✅ Attach trace to auto-enable/disable the dropdown based on fit_option
        self.fit_option.trace_add("write", lambda *args: self._toggle_data_type_dropdown())

    def _toggle_data_type_dropdown(self):
        """ Enables data type dropdown only when 'Linear Spline' is selected. """
        if self.fit_option.get() == "linear spline":
            self.data_type_dropdown.config(state="normal")
        else:
            self.data_type_dropdown.config(state="disabled")
            self.data_type_selection.set("Modified Data")  # ✅ Reset to default

    def toggle_range_controls(self):
        """ Enable/Disable range filter controls based on checkbox state. """
        state = "normal" if self.apply_range_filter.get() else "disabled"
        self.column_dropdown.config(state=state)
        self.min_entry.config(state=state)
        self.max_entry.config(state=state)

        # Ensure the dropdown is populated when enabling the filter
        if self.apply_range_filter.get():
            dataset = self.app_context.data_manager.get_dataset(self.dataset_type)
            if dataset is not None:
                self.update_column_dropdown(dataset.columns.tolist())

    # Updates for dropdown menus

    def update_column_dropdown(self, column_names):
        """ Updates the dropdown menu with available column names. """
        self.column_dropdown["menu"].delete(0, "end")  # Clear existing options

        if column_names:
            for col in column_names:
                self.column_dropdown["menu"].add_command(
                    label=col, command=lambda value=col: self.selected_column.set(value)
                )
            self.selected_column.set(column_names[0])  # Set the first column as default
        else:
            self.selected_column.set("Select Column")  # Reset if no columns are available

    def _update_cycle_column_dropdown(self, selected_column):
        """
        Updates the cycle_column selection dropdown based on the selected cycle column.
        If 'abs_cycle' is selected but 'Compute Absolute Cycle' is not active, it warns the user.
        """
        dataset = self.app_context.data_manager.get_dataset(self.dataset_type)

        if dataset is None:
            messagebox.showerror("Error", f"No {self.dataset_type} dataset loaded.")
            return

        # ✅ Ensure Compute Absolute Cycle is active before allowing 'abs_cycle' selection
        if selected_column == "abs_cycle":
            if self.dataset_type in self.app_context.modify_widgets:
                modify_widget = self.app_context.modify_widgets[self.dataset_type]
                if not modify_widget.compute_abs_cycle.get():
                    messagebox.showwarning("Warning", "Please enable 'Compute Absolute Cycle' before selecting 'abs_cycle'.")
                    return  # ✅ Prevents changing the dropdown if condition is not met

        # ✅ Extract unique cycle values if the column exists
        if selected_column in dataset.columns:
            unique_cycles = sorted(dataset[selected_column].dropna().unique())
            self.update_cycle_options(unique_cycles)

    # Toggle for cycle and cycle_column dropdown menus 
    def _toggle_cycle_dropdowns(self):   #hkw
        """
        Enable or disable the cycle and cycle_column dropdown based on the Select Cycle checkbox.
        """
        if self.select_cycle.get():
            self.cycle_dropdown.config(state="normal")
#            self.cycle_column_dropdown.config(state="normal")
        else:
            self.cycle_dropdown.config(state="disabled")
            self.cycle_column_dropdown.config(state="disabled")

    def toggle_cycle_column_dropdown(self):
        """
        Enables or disables 'abs_cycle' in the dropdown based on 'Compute Absolute Cycle' checkbox.
        If deactivated, resets cycle_column to 'Cyc-Count' and disables the dropdown.
        """
        modify_widget = self.app_context.modify_widgets[self.dataset_type]

        if modify_widget.compute_abs_cycle.get():
            self.cycle_column_dropdown.config(state="normal")
        else:
            self.cycle_column.set("Cyc-Count")  # ✅ Reset to default
            self.cycle_column_dropdown.config(state="disabled")  # ✅ Disable dropdown

    # toggle for use_step_size checkbox
    def _toggle_use_step_size_checkbox(self):
        """
        Enables 'Use Step Size' checkbox only when 'Linear Spline' is selected.
        """
        if self.fit_option.get() == "linear spline":
            self.step_size_checkbox.config(state="normal")  # Enable checkbox
        else:
            self.step_size_checkbox.config(state="disabled")  # Disable checkbox
            self.use_step_size.set(False)  # Uncheck checkbox
            self.step_size_entry.config(state="disabled")  # Disable entry field

    def _toggle_step_size_entryfield(self):
        """
        Enables/disables the step size entry field based on checkbox state.
        """
        if self.use_step_size.get():
            self.step_size_entry.config(state="normal")  # Enable entry field
        else:
            self.step_size_entry.config(state="disabled")  # Disable entry field

    # update options for cycle_column dropdown
    def update_cycle_options(self, cycles):
        """
        Updates the cycle dropdown options based on the dataset.
        """
        menu = self.cycle_dropdown["menu"]
        menu.delete(0, "end")  # Clear existing options
        menu.add_command(label="All", command=lambda: self.cycle_selection.set("All"))  # Add "All" option
        
        for cycle in sorted(cycles):
            menu.add_command(label=str(cycle), command=lambda c=cycle: self.cycle_selection.set(str(c)))

        # ✅ Ensure the first cycle is pre-selected
        if cycles:
            self.cycle_selection.set(str(cycles[0]))
        else:
            self.cycle_selection.set("All")  # Default to "All" if no cycles exist

### plot save store modified data --> should be moved out of FilterWidget sometimes as it works on all data modifications (maybe class ExportModifiedData?)

    def _plot_filtered_data(self):
        """
        Plot the filtered data for the dataset.
        """
        if hasattr(self.app_context.data_manager, "plot_filtered_data"):
            self.app_context.data_manager.plot_filtered_data(self.dataset_type)
        else:
            messagebox.showerror("Error", "Plotting functionality is not available.")

    def _save_filtered_data(self):
        """
        Save the filtered dataset to a file.
        """
        if hasattr(self.app_context.data_manager, "save_filtered_data"):
            self.app_context.data_manager.save_filtered_data(self.dataset_type)
        else:
            messagebox.showerror("Error", "Save functionality is not available.")

    def _store_filtered_data(self):
        """
        Store the filtered dataset for further use.
        """
        if hasattr(self.app_context.data_manager, "store_filtered_data"):
            self.app_context.data_manager.store_filtered_data(self.dataset_type)
        else:
            messagebox.showerror("Error", "Store functionality is not available.")

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

        # Data Modification UI Elements
        tk.Checkbutton(self.frame, text="Compute dU/dQ", variable=self.compute_du_dq, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)
        tk.Checkbutton(self.frame, text="Compute Absolute Cycle", variable=self.compute_abs_cycle, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)
        tk.Checkbutton(self.frame, text="Normalize Voltage", variable=self.normalize_voltage, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)
        # ✅ Attach trace to automatically update the `abs_cycle` selection state
        self.compute_abs_cycle.trace_add("write", lambda *args: self.app_context.filter_widgets[self.dataset_type].toggle_cycle_column_dropdown())

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
        self.app_context.data_manager.extract_key_values(self.dataset_type)

# widgets for databrowser section

class FilteredDataBrowser:
    def __init__(self, parent, label, dataset_type, app_context):
        self.app_context = app_context
        self.dataset_type = dataset_type

        # Create a frame for the browser
        self.frame = tk.LabelFrame(parent, text=label, font=UIStyling.LABEL_FONT)
    #    self.frame.pack(side="left", fill="both", expand=True, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)
        self.frame.pack(side="left", fill="x", expand=True, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        # Listbox to show datasets
        self.listbox = tk.Listbox(self.frame, selectmode="multiple", height=UIStyling.LISTBOX_HEIGHT)
       # self.listbox.pack(side="left", fill="both", expand=True, padx=UIStyling.LISTBOX_PADX, pady=UIStyling.LISTBOX_PADY)
        self.listbox.pack(fill="both", expand=True, padx=UIStyling.LISTBOX_PADX, pady=UIStyling.LISTBOX_PADY)


        # Scrollbar for the listbox
        scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Buttons for functionality
        tk.Button(self.frame, text="Select for Plot", command=self._toggle_selection, font=UIStyling.BUTTON_FONT).pack(pady=5)
        tk.Button(self.frame, text="Show Data Table", command=self._show_data_table, font=UIStyling.BUTTON_FONT).pack(pady=5)

    def _show_data_table(self):
        """
        Display the selected dataset in a new window.
        """
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "No dataset selected.")
            return

        dataset_name = self.listbox.get(selected[0]).replace(" [Selected]", "")
        dataset = self.app_context.multi_data_processor.get_dataset_by_name(dataset_name, self.dataset_type)

        if dataset is None:
            messagebox.showerror("Error", "Failed to retrieve the selected dataset.")
            return

        self._display_dataset_table(dataset, dataset_name)

    def _display_dataset_table(self, dataset, dataset_name):
        """
        Helper function to display a dataset in a new window.
        """
        table_window = tk.Toplevel(self.app_context.root)
        table_window.title(f"Data Table - {dataset_name}")
        table_window.geometry("800x600")

        x_scrollbar = tk.Scrollbar(table_window, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")

        y_scrollbar = tk.Scrollbar(table_window, orient="vertical")
        y_scrollbar.pack(side="right", fill="y")

        text = tk.Text(table_window, wrap="none", xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
        text.pack(side="left", fill="both", expand=True)

        x_scrollbar.config(command=text.xview)
        y_scrollbar.config(command=text.yview)

        # Insert the dataset as a string
        text.insert("1.0", dataset.to_string(index=False))

    def add_dataset(self, dataset_name):
        """
        Add a dataset to the browser.
        """
        self.listbox.insert(tk.END, dataset_name)

    def get_selected_datasets(self):
        """
        Get the selected datasets from the browser.
        """
        return [
            self.listbox.get(idx).replace(" [Selected]", "")
            for idx in range(self.listbox.size())
            if self.listbox.get(idx).endswith("[Selected]")
        ]

    def clear_browser(self):
        """
        Clear all datasets from the browser.
        """
        self.listbox.delete(0, tk.END)

    def _toggle_selection(self):
        """
        Mark or unmark the selected datasets as [Selected].
        """
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "No datasets selected.")
            return

        for idx in selected_indices:
            item = self.listbox.get(idx)
            if "[Selected]" in item:
                # Remove the [Selected] tag
                self.listbox.delete(idx)
                self.listbox.insert(idx, item.replace(" [Selected]", ""))
                self.listbox.itemconfig(idx, {"fg": "black"})
            else:
                # Add the [Selected] tag
                self.listbox.delete(idx)
                self.listbox.insert(idx, f"{item} [Selected]")
                self.listbox.itemconfig(idx, {"fg": "green"})
