import tkinter as tk
from tkinter import messagebox
from ui_widgets import UIStyling

class ModifyDataWidget:
    """
    A widget for modifying datasets with additional computed columns.
    """
    def __init__(self, parent, label_text, dataset_type, app_context):
        self.app_context = app_context
        self.dataset_type = dataset_type

        self.frame = tk.LabelFrame(parent, text=label_text, font=("Arial", 10))
        self.frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.compute_du_dq = tk.BooleanVar()
        self.compute_abs_cycle = tk.BooleanVar()
        self.normalize_voltage = tk.BooleanVar()

        # Modification options
        tk.Checkbutton(self.frame, text="Compute dU/dQ", variable=self.compute_du_dq).pack(anchor="w", padx=5, pady=2)
        tk.Checkbutton(self.frame, text="Compute Absolute Cycle", variable=self.compute_abs_cycle).pack(anchor="w", padx=5, pady=2)
        tk.Checkbutton(self.frame, text="Normalize Voltage", variable=self.normalize_voltage).pack(anchor="w", padx=5, pady=2)

        # **No more Apply Modifications or Show Data buttons!**

    def _apply_modifications(self):
        """
        Apply selected modifications to the dataset and add new columns.
        """
        if self.dataset_type not in self.app_context.datasets:
            messagebox.showerror("Error", f"No {self.dataset_type} dataset loaded.")
            return

        dataset = self.app_context.datasets[self.dataset_type]["data"]
        if dataset is None:
            messagebox.showerror("Error", f"No {self.dataset_type} dataset loaded.")
            return

        modified_data = dataset.copy()

        # Compute dU/dQ if selected
        if self.compute_du_dq.get():
            if "Ah-Cyc-Charge-0" not in dataset.columns or "U[V]" not in dataset.columns:
                messagebox.showerror(
                    "Error", f"Dataset is missing required columns for dU/dQ calculation."
                )
                return
            modified_data["dU/dQ"] = (
                modified_data["U[V]"].diff() / modified_data["Ah-Cyc-Charge-0"].diff()
            )

        # Compute Absolute Cycle if selected
        if self.compute_abs_cycle.get():
            modified_data = self.app_context.compute_absolute_cycle(modified_data)  # Use the corrected function

        # Store the modified dataset
        dataset_name = f"{self.dataset_type}_modified"
        self.app_context.filtered_datasets[self.dataset_type].append(
            {"name": dataset_name, "data": modified_data}
        )
        self.app_context.anode_browser.add_dataset(dataset_name) if self.dataset_type == "anode" else self.app_context.cathode_browser.add_dataset(dataset_name)

        messagebox.showinfo("Success", f"Modifications applied to {self.dataset_type} dataset.")

    def _show_modified_data(self):
        """
        Show the modified dataset in a table.
        """
        self.app_context._show_modified_data(self.dataset_type)

class FilterWidget:
    """
    Widget for handling filter options and visualization types.
    """
    def __init__(self, parent, label_text, dataset_type, app_context):
        self.app_context = app_context
        self.dataset_type = dataset_type

        # Main frame with centralized styling
        self.frame = tk.LabelFrame(parent, text=label_text, font=UIStyling.LABEL_FONT)
        self.frame.grid(row=0, column=0 if dataset_type == "anode" else 1, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY, sticky="nsew")

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

        self._create_filter_options()

        # Add buttons with centralized styling
        tk.Button(self.frame, text="Plot Filtered Data", command=self._plot_filtered_data, font=UIStyling.BUTTON_FONT).grid(row=1, column=0, padx=UIStyling.FRAME_PADX, pady=5, sticky="w")
        tk.Button(self.frame, text="Save Filtered Data", command=self._save_filtered_data, font=UIStyling.BUTTON_FONT).grid(row=1, column=1, padx=UIStyling.FRAME_PADX, pady=5, sticky="w")
        tk.Button(self.frame, text="Store Filtered Data", command=self._store_filtered_data, font=UIStyling.BUTTON_FONT).grid(row=1, column=2, padx=UIStyling.FRAME_PADX, pady=5, sticky="w")

    def _create_filter_options(self):
        # Filter Criteria
        filter_frame = tk.LabelFrame(self.frame, text="Select filter criteria", font=UIStyling.LABEL_FONT)
        filter_frame.grid(row=0, column=0, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY, sticky="nsew")

        tk.Checkbutton(filter_frame, text="Remove pause", variable=self.remove_pause, font=UIStyling.LABEL_FONT).pack(anchor="w", padx=5, pady=2)

        # Cycle selection
        cycle_frame = tk.Frame(filter_frame)
        cycle_frame.pack(anchor="w", padx=5, pady=2)
        tk.Checkbutton(cycle_frame, text="Select cycle", variable=self.select_cycle, command=self._toggle_cycle_dropdown, font=UIStyling.LABEL_FONT).pack(side="left")
        self.cycle_dropdown = tk.OptionMenu(cycle_frame, self.cycle_selection, "")
        self.cycle_dropdown.pack(side="left")
        self.cycle_dropdown.config(state="disabled")

        tk.Checkbutton(filter_frame, text="Select charge half cycle", variable=self.select_charge_half_cycle, font=UIStyling.LABEL_FONT).pack(anchor="w", padx=5, pady=2)
        tk.Checkbutton(filter_frame, text="Select discharge half cycle", variable=self.select_discharge_half_cycle, font=UIStyling.LABEL_FONT).pack(anchor="w", padx=5, pady=2)

        # Step Change Filter UI
        step_change_frame = tk.Frame(filter_frame)
        step_change_frame.pack(anchor="w", padx=5, pady=2)

        tk.Checkbutton(step_change_frame, text="Apply Step Change Filter", variable=self.apply_step_change, font=UIStyling.LABEL_FONT).pack(side="left")
        self.step_change_dropdown = tk.OptionMenu(step_change_frame, self.step_change_column, "Line", "Command", "Cyc-Count")
        self.step_change_dropdown.pack(side="left")

        # Plot Type Selection
        plot_frame = tk.LabelFrame(self.frame, text="Select plot type", font=UIStyling.LABEL_FONT)
        plot_frame.grid(row=0, column=1, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY, sticky="nsew")

        tk.Radiobutton(plot_frame, text="U vs t (Voltage-Time)", variable=self.plot_option, value="U-t", font=UIStyling.LABEL_FONT).pack(anchor="w", padx=5)
        tk.Radiobutton(plot_frame, text="I vs t (Current-Time)", variable=self.plot_option, value="I-t", font=UIStyling.LABEL_FONT).pack(anchor="w", padx=5)
        tk.Radiobutton(plot_frame, text="Q vs U (Charge-Voltage)", variable=self.plot_option, value="Q-U", font=UIStyling.LABEL_FONT).pack(anchor="w", padx=5)

        # Fit Type Selection
        fit_frame = tk.LabelFrame(self.frame, text="Select fit type", font=UIStyling.LABEL_FONT)
        fit_frame.grid(row=0, column=2, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY, sticky="nsew")

        tk.Radiobutton(fit_frame, text="No Fit", variable=self.fit_option, value="no fit", font=UIStyling.LABEL_FONT).pack(anchor="w", padx=5)
        tk.Radiobutton(fit_frame, text="Linear Spline", variable=self.fit_option, value="linear spline", font=UIStyling.LABEL_FONT).pack(anchor="w", padx=5)

        # Visualization Options
        visualization_frame = tk.LabelFrame(self.frame, text="Select visualization type", font=UIStyling.LABEL_FONT)
        visualization_frame.grid(row=0, column=3, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY, sticky="nsew")

        tk.Checkbutton(visualization_frame, text="Show Key Values", variable=self.visualize_key_values, font=UIStyling.LABEL_FONT).pack(anchor="w", padx=5)
        tk.Checkbutton(visualization_frame, text="Show Cycles", variable=self.show_cycles, font=UIStyling.LABEL_FONT).pack(anchor="w", padx=5)

    def _toggle_cycle_dropdown(self):
        """
        Enable or disable the cycle dropdown based on the Select Cycle checkbox.
        """
        if self.select_cycle.get():
            self.cycle_dropdown.config(state="normal")
        else:
            self.cycle_dropdown.config(state="disabled")

    def _plot_filtered_data(self):
        self.app_context.plot_filtered_data(self.dataset_type)

    def _save_filtered_data(self):
        self.app_context.save_filtered_data(self.dataset_type)

    def _store_filtered_data(self):
        self.app_context.store_filtered_data(self.dataset_type)

class KeyValuesWidget:
    """
    Widget for handling the extraction of key values for anode/cathode datasets.
    """
    def __init__(self, parent, label_text, dataset_type, app_context):
        self.app_context = app_context
        self.dataset_type = dataset_type

        self.frame = tk.LabelFrame(parent, text=label_text, font=("Arial", 10))
        self.frame.grid(row=1, column=0 if dataset_type == "anode" else 1, padx=10, pady=10, sticky="nsew")

        self.extract_max_voltage = tk.BooleanVar()
        self.extract_max_charge = tk.BooleanVar()
        self.extract_max_discharge = tk.BooleanVar()

        # Key Value Checkboxes
        tk.Checkbutton(self.frame, text="Max Voltage", variable=self.extract_max_voltage).pack(anchor="w", padx=5, pady=2)
        tk.Checkbutton(self.frame, text="Max Ah-Cyc-Charge-0", variable=self.extract_max_charge).pack(anchor="w", padx=5, pady=2)
        tk.Checkbutton(self.frame, text="Max Ah-Cyc-Discharge-0", variable=self.extract_max_discharge).pack(anchor="w", padx=5, pady=2)

        # Extract Button
        tk.Button(self.frame, text="Extract Key Values", command=self._extract_key_values).pack(pady=10)

    def _extract_key_values(self):
        """
        Extract key values for the dataset.
        """
        self.app_context.extract_key_values(self.dataset_type)
