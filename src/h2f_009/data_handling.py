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

        # Modification options
        tk.Checkbutton(self.frame, text="Compute dU/dQ", variable=self.compute_du_dq, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)
        tk.Checkbutton(self.frame, text="Compute Absolute Cycle", variable=self.compute_abs_cycle, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)
        tk.Checkbutton(self.frame, text="Normalize Voltage", variable=self.normalize_voltage, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)

        # **Offset Modification UI**
        offset_frame = tk.Frame(self.frame)
        offset_frame.pack(fill="x", pady=5)

        tk.Label(offset_frame, text="Offset Column:").pack(side="left", padx=5)
        self.selected_column = tk.StringVar(value="")  # Stores selected column
        self.column_dropdown = tk.OptionMenu(offset_frame, self.selected_column, "")
        self.column_dropdown.pack(side="left", padx=5)

        tk.Label(offset_frame, text="Offset Value:").pack(side="left", padx=5)
        self.offset_value = tk.DoubleVar(value=0.0)  # Default offset is 0
        self.offset_entry = tk.Entry(offset_frame, textvariable=self.offset_value, width=7)
        self.offset_entry.pack(side="left", padx=5)

        # **Apply Modifications Button**
        tk.Button(self.frame, text="Apply Modifications", command=self.apply_modifications).pack(pady=5)

    def apply_modifications(self):
            """
            Triggers the dataset modification in the main application.
            """
            self.app.modify_dataset(self.dataset_type)

    def update_column_dropdown(self, column_names):
        """
        Updates the dropdown with available column names.
        """
        self.column_dropdown["menu"].delete(0, "end")  # Clear previous entries
        for col in column_names:
            self.column_dropdown["menu"].add_command(label=col, command=tk._setit(self.selected_column, col))
        if column_names:
            self.selected_column.set(column_names[0])  # Default to first column

class FilterWidget:
    """
    Widget for handling filter options and visualization types.
    """
    def __init__(self, parent, label_text, dataset_type, app_context):
        self.app_context = app_context
        self.dataset_type = dataset_type

        self.frame = tk.LabelFrame(parent, text=label_text, font=UIStyling.LABEL_FONT)
        #self.frame.grid(row=0, column=0 if dataset_type == "anode" else 1, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY, sticky="nsew")
        self.frame.pack(fill="both", expand=True, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        self.remove_pause = tk.BooleanVar()
        self.select_cycle = tk.BooleanVar()
        self.select_charge_half_cycle = tk.BooleanVar()
        self.select_discharge_half_cycle = tk.BooleanVar()

        # Step Change Filter
        self.apply_step_change = tk.BooleanVar()
        self.step_change_column = tk.StringVar(value="Line")  # Default column
        
        self.plot_option = tk.StringVar(value="U-t")
        self.fit_option = tk.StringVar(value="no fit")
        self.visualize_key_values = tk.BooleanVar(value=False)
        self.show_cycles = tk.BooleanVar(value=False)
        self.cycle_selection = tk.StringVar(value="All")
        self.cycle_column_option = tk.StringVar(value="Cyc-Count")  # Default to "Cyc-Count"

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
        # Filter Criteria
        filter_frame = tk.LabelFrame(self.frame, text="Select filter criteria", font=UIStyling.LABEL_FONT)
        # filter_frame.grid(row=0, column=0, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY, sticky="nsew")
        filter_frame.pack(fill="both", expand=True, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        tk.Checkbutton(filter_frame, text="Remove pause", variable=self.remove_pause, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)
        
        # Select Cycle with Dropdown
        cycle_frame = tk.Frame(filter_frame)
        cycle_frame.pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)
        tk.Checkbutton(cycle_frame, text="Select cycle", variable=self.select_cycle, command=self._toggle_cycle_dropdown, font=UIStyling.BUTTON_FONT).pack(side="left")
        self.cycle_dropdown = tk.OptionMenu(cycle_frame, self.cycle_selection, "")
        self.cycle_dropdown.config(font=UIStyling.DROPDOWN_FONT, state="disabled")  # ✅ Apply centralized font
        self.cycle_dropdown.pack(side="left", padx=UIStyling.DROPDOWN_PADX)

        tk.Checkbutton(filter_frame, text="Select charge half cycle", variable=self.select_charge_half_cycle, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)
        tk.Checkbutton(filter_frame, text="Select discharge half cycle", variable=self.select_discharge_half_cycle, font=UIStyling.BUTTON_FONT).pack(anchor="w", padx=UIStyling.LISTBOX_PADX, pady=2)

        # Step Change Filter UI
        step_change_frame = tk.Frame(filter_frame)
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
