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


class FilteredDataBrowser:
    def __init__(self, parent, label, dataset_type, app_context):
        self.app_context = app_context
        self.dataset_type = dataset_type

        # Create a frame for the browser
        self.frame = tk.LabelFrame(parent, text=label, font=("Arial", 10))
        self.frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        # Listbox to show datasets
        self.listbox = tk.Listbox(self.frame, selectmode="multiple", height=10)
        self.listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Scrollbar for the listbox
        scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Buttons for functionality
        tk.Button(self.frame, text="Select for Plot", command=self._toggle_selection).pack(pady=5)
        tk.Button(self.frame, text="Show Data Table", command=self._show_data_table).pack(pady=5)

    def _show_data_table(self):
        """
        Display the selected dataset in a new window.
        """
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "No dataset selected.")
            return

        dataset_name = self.listbox.get(selected[0]).replace(" [Selected]", "")
        dataset = self.app_context._get_dataset_by_name(dataset_name, self.dataset_type)

        if dataset is None:
            messagebox.showerror("Error", "Failed to retrieve the selected dataset.")
            return

        # Display the dataset in a new window
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

class MultiGraphPlotter:
    def __init__(self, app_context):
        self.app_context = app_context
    
    def plot_multi_graph(self):
        """
        Fetch selected datasets from anode, cathode, and full cell browsers
        and plot them in a single figure.
        """
        # Get selected datasets from all three browsers
        anode_datasets = self.app_context.anode_browser.get_selected_datasets()
        cathode_datasets = self.app_context.cathode_browser.get_selected_datasets()
        full_cell_datasets = self.app_context.full_cell_browser.get_selected_datasets()

        # Check if at least one dataset is selected
        if not anode_datasets and not cathode_datasets and not full_cell_datasets:
            messagebox.showerror("Error", "No datasets selected from any browser.")
            return

        # Create the main figure
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Prepare a secondary x-axis for Q-U plots
        ax2 = None
        plot_type = self.app_context.multi_graph_plot_option.get()

        if plot_type == "Q-U (Charge-Voltage)":
            ax2 = ax1.twiny()

        # Plot datasets from the anode browser
        for dataset_name in anode_datasets:
            dataset = self.app_context._get_dataset_by_name(dataset_name, "anode")
            if dataset is not None:
                self._plot_dataset(ax1, ax2, dataset, dataset_name, plot_type, "blue")

        # Plot datasets from the cathode browser
        for dataset_name in cathode_datasets:
            dataset = self.app_context._get_dataset_by_name(dataset_name, "cathode")
            if dataset is not None:
                self._plot_dataset(ax1, ax2, dataset, dataset_name, plot_type, "red")

        # Plot datasets from the full cell browser
        for dataset_name in full_cell_datasets:
            dataset = self.app_context._get_dataset_by_name(dataset_name, "full_cell")
            if dataset is not None:
                if plot_type == "Q-U (Charge-Voltage)":
                    # Ensure full cell datasets are treated appropriately
                    if "Q (Ah)" in dataset.columns and "U_full_cell (V)" in dataset.columns:
                        ax1.plot(
                            dataset["Q (Ah)"], 
                            dataset["U_full_cell (V)"], 
                            label=f"{dataset_name} (Full Cell)", 
                            color="purple"
                        )
                    else:
                        messagebox.showerror(
                            "Error", f"Full cell dataset {dataset_name} is missing required columns."
                        )
                else:
                    self._plot_dataset(ax1, ax2, dataset, dataset_name, plot_type, "purple")

        # Update labels dynamically based on plot type
        xlabel, ylabel = self._get_axis_labels(plot_type)
        ax1.set_xlabel(xlabel)
        ax1.set_ylabel(ylabel)
        ax1.set_title("Multi-Graph Plot")

        # Adjust the legend to avoid overlapping with the graph
        ax1.legend(loc="best", fontsize="small")
        plt.tight_layout()
        plt.grid(True)
        plt.show()

    def _plot_dataset(self, ax1, ax2, dataset, label, plot_type, color):
        """
        Plot a single dataset on the current matplotlib figure based on the selected plot type.
        """
        try:
            if plot_type == "U-t (Voltage-Time)":
                ax1.plot(dataset["Time[h]"], dataset["U[V]"], label=label, color=color)
            elif plot_type == "I-t (Current-Time)":
                ax1.plot(dataset["Time[h]"], dataset["I[A]"], label=label, color=color)
            elif plot_type == "Q-U (Charge-Voltage)":
                # Ensure both columns are present
                if "Ah-Cyc-Charge-0" not in dataset.columns or "Ah-Cyc-Discharge-0" not in dataset.columns:
                    messagebox.showerror("Error", f"Dataset {label} is missing required columns for Q-U plotting.")
                    return
                    
                # Split dataset into charge and discharge parts
                charge_data = dataset[dataset["Command"].str.contains("Charge", na=False)]
                discharge_data = dataset[dataset["Command"].str.contains("Discharge", na=False)]

                # Plot charge data on the main axis
                if not charge_data.empty:
                    ax1.plot(charge_data["Ah-Cyc-Charge-0"], charge_data["U[V]"], label=f"{label} (Charge)", color=color)
                    ax1.set_xlabel("Charge (Ah)")

                # Plot discharge data on the secondary axis
                if ax2 and not discharge_data.empty:
                    ax2.plot(discharge_data["Ah-Cyc-Discharge-0"], discharge_data["U[V]"],
                            label=f"{label} (Discharge)", color=color, linestyle="--")
                    ax2.set_xlabel("Discharge (Ah)")

            elif dataset_type == "full_cell":  # Add this block for full_cell datasets
                if "Ah-Cyc-Charge-0" in dataset.columns and "U[V]" in dataset.columns:
                    ax1.plot(dataset["Ah-Cyc-Charge-0"], dataset["U[V]"], label=label, color="purple")
                    ax1.set_xlabel("Charge (Ah)")
                else:
                    messagebox.showerror("Error", f"Full cell dataset {label} is missing required columns.")
                    return
            else:
                messagebox.showerror("Error", f"Unsupported plot type: {plot_type}")

        except KeyError as e:
            messagebox.showerror("Error", f"Missing required columns in dataset {label}: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to plot dataset {label}: {e}")

    def _get_axis_labels(self, plot_type):
        """
        Returns appropriate axis labels based on the selected plot type.
        """
        if plot_type == "U-t (Voltage-Time)":
            return "Time (h)", "Voltage (V)"
        elif plot_type == "I-t (Current-Time)":
            return "Time (h)", "Current (A)"
        elif plot_type == "Q-U (Charge-Voltage)":
            return "Charge/Discharge (Ah)", "Voltage (V)"
        else:
            return "X-axis", "Y-axis"


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

class FilterWidget:
    """
    Widget for handling filter options and visualization types.
    """
    def __init__(self, parent, label_text, dataset_type, app_context):
        self.app_context = app_context
        self.dataset_type = dataset_type

        self.frame = tk.LabelFrame(parent, text=label_text, font=("Arial", 10))
        self.frame.grid(row=0, column=0 if dataset_type == "anode" else 1, padx=10, pady=10, sticky="nsew")

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

        self._create_filter_options()

        # Add Plot and Save Buttons
        tk.Button(self.frame, text="Plot Filtered Data", command=self._plot_filtered_data).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        tk.Button(self.frame, text="Save Filtered Data", command=self._save_filtered_data).grid(row=1, column=1, padx=10, pady=5, sticky="w")
        tk.Button(self.frame, text="Store Filtered Data", command=self._store_filtered_data).grid(row=1, column=2, padx=10, pady=5, sticky="w")

    def _create_filter_options(self):
        # Filter Criteria
        filter_frame = tk.LabelFrame(self.frame, text="Select filter criteria", font=("Arial", 10))
        filter_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        tk.Checkbutton(filter_frame, text="Remove pause", variable=self.remove_pause).pack(anchor="w", padx=5, pady=2)
        
        # Select Cycle with Dropdown
        cycle_frame = tk.Frame(filter_frame)
        cycle_frame.pack(anchor="w", padx=5, pady=2)
        tk.Checkbutton(cycle_frame, text="Select cycle", variable=self.select_cycle, command=self._toggle_cycle_dropdown).pack(side="left")
        self.cycle_dropdown = tk.OptionMenu(cycle_frame, self.cycle_selection, "")
        self.cycle_dropdown.pack(side="left")
        self.cycle_dropdown.config(state="disabled")  # Initially disabled

        tk.Checkbutton(filter_frame, text="Select charge half cycle", variable=self.select_charge_half_cycle).pack(anchor="w", padx=5, pady=2)
        tk.Checkbutton(filter_frame, text="Select discharge half cycle", variable=self.select_discharge_half_cycle).pack(anchor="w", padx=5, pady=2)

        # Step Change Filter UI
        step_change_frame = tk.Frame(filter_frame)
        step_change_frame.pack(anchor="w", padx=5, pady=2)

        tk.Checkbutton(step_change_frame, text="Apply Step Change Filter", variable=self.apply_step_change).pack(side="left")
        self.step_change_dropdown = tk.OptionMenu(step_change_frame, self.step_change_column, "Line", "Command", "Cyc-Count")
        self.step_change_dropdown.pack(side="left")

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

        # Visualization Options (WITH CYCLE COLUMN SELECTION)
        visualization_frame = tk.LabelFrame(self.frame, text="Select visualization type", font=("Arial", 10))
        visualization_frame.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")

        tk.Checkbutton(visualization_frame, text="Show Key Values", variable=self.visualize_key_values).pack(anchor="w", padx=5)
        tk.Checkbutton(visualization_frame, text="Show Cycles", variable=self.show_cycles).pack(anchor="w", padx=5)

        # **Cycle Column Selection Dropdown (New)**
        self.cycle_column_option = tk.StringVar(value="Cyc-Count")
        tk.Label(visualization_frame, text="Cycle Column:").pack(anchor="w", padx=5, pady=2)
        tk.OptionMenu(visualization_frame, self.cycle_column_option, "Cyc-Count", "abs_cycle").pack(anchor="w", padx=5)


    def _toggle_cycle_dropdown(self):
        """
        Enable or disable the cycle dropdown based on the Select Cycle checkbox.
        """
        if self.select_cycle.get():
            self.cycle_dropdown.config(state="normal")
        else:
            self.cycle_dropdown.config(state="disabled")

    def populate_cycle_dropdown(self, cycles):
        """
        Populate the cycle dropdown with available cycle numbers.
        """
        menu = self.cycle_dropdown["menu"]
        menu.delete(0, "end")  # Clear current options
        for cycle in cycles:
            menu.add_command(label=cycle, command=lambda value=cycle: self.cycle_selection.set(value))

    def update_step_change_options(self, columns):
        """
        Updates the dropdown menu with available columns for step change filtering.
        """
        menu = self.step_change_dropdown["menu"]
        menu.delete(0, "end")  # Clear existing options
        for col in columns:
            menu.add_command(label=col, command=lambda c=col: self.step_change_column.set(c))

    def update_cycle_options(self, cycles):
        """
        Updates the cycle dropdown options based on the dataset.
        """
        menu = self.cycle_dropdown["menu"]
        menu.delete(0, "end")  # Clear existing options
        menu.add_command(label="All", command=lambda: self.cycle_selection.set("All"))  # Add "All" option
        for cycle in sorted(cycles):
            menu.add_command(label=str(cycle), command=lambda c=cycle: self.cycle_selection.set(str(c)))

    def _plot_filtered_data(self):
        self.app_context.plot_filtered_data(self.dataset_type)

    def _save_filtered_data(self):
        self.app_context.save_filtered_data(self.dataset_type)

    def _store_filtered_data(self):
        self.app_context.store_filtered_data(self.dataset_type)
   
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
        self.filtered_datasets = {"anode": [], "cathode": [], "full_cell": []}
        # Store only the latest modified dataset
        self.modified_datasets = {"anode": None, "cathode": None}

        # Add multi-plot type attribute
        self.multi_plot_type = tk.StringVar(value="U-t (Voltage-Time)")

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

        # Add buttons for saving and loading projects and showing loaded plots
        tk.Button(self.main_frame, text="Save Project", command=self.save_project_callback).pack(pady=5)
        tk.Button(self.main_frame, text="Load Project", command=self.load_project_callback).pack(pady=5)
        tk.Button(self.main_frame, text="Show Loaded Plots", command=self.show_loaded_plots).pack(pady=5)

        # Half Cell Data Section
        tk.Label(self.main_frame, text="Half cell data", font=("Arial", 12, "underline")).pack(pady=5)
        data_section = tk.Frame(self.main_frame)
        data_section.pack(fill="x", padx=10, pady=5)

        self.anode_widget = DataWidget(data_section, "Anode", "anode", self)
        self.cathode_widget = DataWidget(data_section, "Cathode", "cathode", self)

        # Filter Sections
        filter_section = tk.Frame(self.main_frame)
        filter_section.pack(fill="x", padx=10, pady=5)

        self.anode_filter_widget = FilterWidget(filter_section, "Filter Anode Data", "anode", self)
        self.cathode_filter_widget = FilterWidget(filter_section, "Filter Cathode Data", "cathode", self)

        # Key Values Sections
        key_values_section = tk.Frame(self.main_frame)
        key_values_section.pack(fill="x", padx=10, pady=5)

        self.anode_key_values_widget = KeyValuesWidget(key_values_section, "Extract Anode Key Values", "anode", self)
        self.cathode_key_values_widget = KeyValuesWidget(key_values_section, "Extract Cathode Key Values", "cathode", self)

        # Modify Data Sections
        modify_data_frame = tk.Frame(self.main_frame)
        modify_data_frame.pack(fill="x", padx=10, pady=5)

        self.anode_modify_widget = ModifyDataWidget(modify_data_frame, "Modify Anode Data", "anode", self)
        self.cathode_modify_widget = ModifyDataWidget(modify_data_frame, "Modify Cathode Data", "cathode", self)

        # Filtered Data Browsers
        browser_section = tk.Frame(self.main_frame)
        browser_section.pack(fill="x", padx=10, pady=5)

        self.anode_browser = FilteredDataBrowser(browser_section, "Filtered Anode Data Browser", "anode", self)
        self.cathode_browser = FilteredDataBrowser(browser_section, "Filtered Cathode Data Browser", "cathode", self)
        self.full_cell_browser = FilteredDataBrowser(browser_section, "Full Cell Data Browser", "full_cell", self)

        # Add a button for calculating full cell voltage
        tk.Button(
            self.main_frame, 
            text="Calculate Full Cell Voltage", 
            command=self.calculate_full_cell_voltage
        ).pack(pady=10)

        # Multi-Graph Plot Section
        tk.Label(self.main_frame, text="Multi-Graph Plot", font=("Arial", 12, "underline")).pack(pady=5)

        # Frame for plot type selection and button
        multi_graph_frame = tk.Frame(self.main_frame)
        multi_graph_frame.pack(pady=10)

        # Dropdown for selecting plot type
        tk.Label(multi_graph_frame, text="Select Plot Type:").pack(side="left", padx=5)
        self.multi_graph_plot_option = tk.StringVar(value="U-t (Voltage-Time)")
        plot_options = ["U-t (Voltage-Time)", "I-t (Current-Time)", "Q-U (Charge-Voltage)"]
        tk.OptionMenu(multi_graph_frame, self.multi_graph_plot_option, *plot_options).pack(side="left", padx=5)

        # Plot Multi-Graph Button
        tk.Button(multi_graph_frame, text="Plot Multi-Graph", command=self._plot_multi_graph).pack(side="left", padx=10)

    def initialize_dataset_from_project(self, dataset_type, dataset_df, file_name):
        """
        Properly initializes a dataset after loading it from a project file.
        Ensures the dataset is fully available in the UI just like when loading manually.
        """
        if dataset_df is None:
            messagebox.showerror("Error", f"Failed to initialize {dataset_type} dataset.")
            return

        # ✅ Store dataset in memory
        self.datasets[dataset_type]["data"] = dataset_df
        self.datasets[dataset_type]["file_path"].set(file_name)  # ✅ Update UI label

        # ✅ Update UI elements (file path label)
        if dataset_type == "anode":
            self.anode_widget.file_label.config(text=file_name)
        else:
            self.cathode_widget.file_label.config(text=file_name)

        # ✅ Update cycle dropdown options if 'Cyc-Count' column exists
        if "Cyc-Count" in dataset_df.columns:
            unique_cycles = sorted(dataset_df["Cyc-Count"].unique())
            if dataset_type == "anode":
                self.anode_filter_widget.update_cycle_options(unique_cycles)
            else:
                self.cathode_filter_widget.update_cycle_options(unique_cycles)

        print(f"✅ Successfully initialized {dataset_type} dataset from project: {file_name}")


    def save_project_callback(self):
        """
        Opens a file dialog for saving the project.
        """
        save_folder = os.path.join(os.getcwd(), "projects")
        os.makedirs(save_folder, exist_ok=True)

        file_path = filedialog.asksaveasfilename(
            defaultextension=".hc2fcproj",
            filetypes=[("HC2FC Project Files", "*.hc2fcproj")],
            title="Save Project",
            initialdir=save_folder
        )
        if file_path:
            self.save_project(file_path)


    def save_project(self, project_path):
        """
        Saves the project as a .hc2fcproj ZIP file containing JSON metadata and stored datasets.
        """
        try:
            project_data = {
                "original_files": {
                    "anode": os.path.splitext(self.datasets["anode"]["file_path"].get())[0] + ".txt",
                    "cathode": os.path.splitext(self.datasets["cathode"]["file_path"].get())[0] + ".txt"
                },
                "datasets": {dtype: [ds["name"] for ds in self.filtered_datasets[dtype]]
                             for dtype in ["anode", "cathode", "full_cell"]}
            }

            with zipfile.ZipFile(project_path, "w", zipfile.ZIP_DEFLATED) as project_zip:
                project_zip.writestr("project_metadata.json", json.dumps(project_data, indent=4))

                for dtype in ["anode", "cathode"]:
                    file_name = self.datasets[dtype]["file_path"].get()
                    dataset = self.datasets[dtype]["data"]

                    if dataset is not None and file_name != "No file selected":
                        dataset_txt = dataset.to_csv(index=False, sep="\t")
                        project_zip.writestr(f"datasets/{file_name}.txt", dataset_txt)

                for dtype, datasets in self.filtered_datasets.items():
                    for dataset in datasets:
                        dataset_txt = dataset["data"].to_csv(index=False, sep="\t")
                        project_zip.writestr(f"datasets/{dataset['name']}.txt", dataset_txt)

            print(f"✅ Project saved successfully: {project_path}")

        except Exception as e:
            print(f"❌ Error saving project: {e}")

  
    def load_project_callback(self):
        """
        Opens a file dialog to select a project file.
        """
        file_path = filedialog.askopenfilename(
            filetypes=[("HC2FC Project Files", "*.hc2fcproj")],
            title="Load Project"
        )
        if file_path:
            self.load_project(file_path)


    def load_project(self, project_path):
        """
        Loads a .hc2fcproj file, restoring datasets.
        """
        try:
            with zipfile.ZipFile(project_path, "r") as project_zip:
                if "project_metadata.json" not in project_zip.namelist():
                    print("❌ Error: Missing metadata file.")
                    return

                metadata_json = project_zip.read("project_metadata.json").decode()
                project_data = json.loads(metadata_json)

                self.datasets = {
                    "anode": {"data": None, "file_path": tk.StringVar(value="No file selected")},
                    "cathode": {"data": None, "file_path": tk.StringVar(value="No file selected")},
                }
                self.filtered_datasets = {"anode": [], "cathode": [], "full_cell": []}

                for dtype in ["anode", "cathode"]:
                    file_name = project_data["original_files"].get(dtype)
                    dataset_txt_path = f"datasets/{file_name}.txt"

                    if dataset_txt_path in project_zip.namelist():
                        with project_zip.open(dataset_txt_path) as dataset_file:
                            dataset_df = pd.read_csv(dataset_file, delimiter="\t")

                            self.datasets[dtype]["data"] = dataset_df
                            self.datasets[dtype]["file_path"].set(file_name)

                    else:
                        print(f"⚠️ Warning: {dtype} dataset '{file_name}' not found.")

                print("✅ Datasets restored.")

                for dtype, dataset_names in project_data["datasets"].items():
                    for dataset_name in dataset_names:
                        dataset_txt_path = f"datasets/{dataset_name}.txt"
                        if dataset_txt_path in project_zip.namelist():
                            with project_zip.open(dataset_txt_path) as dataset_file:
                                dataset_df = pd.read_csv(dataset_file, delimiter="\t")

                                self.filtered_datasets[dtype].append({"name": dataset_name, "data": dataset_df})

                print("✅ Filtered datasets restored.")

        except Exception as e:
            print(f"❌ Error loading project: {e}")

    def select_file(self, dataset_type):
        """
        Allows the user to select a file and updates the dataset.
        """
        initial_dir = os.path.join(os.getcwd(), "data")
        file_path = filedialog.askopenfilename(
            title=f"Select {dataset_type.capitalize()} Data File",
            filetypes=[("Text Files", "*.txt")],  # Only allow .txt files
            initialdir=initial_dir,
        )
        if file_path:
            try:
                data = pd.read_csv(file_path, skiprows=12, delimiter="\t", encoding="utf-8", on_bad_lines="skip")
                self.datasets[dataset_type]["data"] = data
                self.datasets[dataset_type]["file_path"].set(os.path.basename(file_path))

                messagebox.showinfo("Success", f"{dataset_type.capitalize()} dataset loaded.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load {dataset_type} dataset: {e}")

    def save_filtered_data(self, dataset_type):
        """
        Saves the filtered data as a .txt file.
        """
        filtered_data = self.datasets[dataset_type]["data"]
        if filtered_data is None:
            messagebox.showerror("Error", f"No {dataset_type} dataset loaded.")
            return

        save_folder = os.path.join(os.getcwd(), "filtered_data")
        os.makedirs(save_folder, exist_ok=True)

        suggested_filename = f"{dataset_type}_filtered.txt"

        save_path = filedialog.asksaveasfilename(
            title="Save Filtered Data",
            initialdir=save_folder,
            initialfile=suggested_filename,
            filetypes=[("Text Files", "*.txt")]
        )

        if save_path:
            try:
                filtered_data.to_csv(save_path, index=False, sep="\t")
                messagebox.showinfo("Success", f"Filtered data saved: {save_path}.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save filtered data: {e}")

    def show_loaded_plots(self):
        """
        Displays all restored plots in separate windows.
        """
        if not hasattr(self, "loaded_plots") or not self.loaded_plots:
            messagebox.showerror("Error", "No plots were loaded from the project file.")
            return

        for i, image in enumerate(self.loaded_plots):
            plot_window = tk.Toplevel(self.root)
            plot_window.title(f"Restored Plot {i+1}")
            plot_window.geometry("600x400")

            img_tk = ImageTk.PhotoImage(image)
            label = tk.Label(plot_window, image=img_tk)
            label.image = img_tk  # Keep reference to avoid garbage collection
            label.pack()

        print("Displayed loaded plots.")

    def step_change_filter(self, df, column):
        """
        Keeps only the last row before the value in 'column' changes.
        """
        if column not in df.columns:
            messagebox.showerror("Error", f"Column '{column}' not found in dataset.")
            return df  # Return unmodified dataset to prevent breaking

        # Identify rows where the column value changes
        df["shifted"] = df[column].shift(-1)  # Shift column to compare with the next row
        filtered_df = df[df[column] != df["shifted"]].drop(columns=["shifted"])  # Keep last row before change
        
        return filtered_df

    def compute_absolute_cycle(self, dataset):
        """
        Computes the absolute cycle count based on 'Cyc-Count'.
        Ensures:
        - Cycles remain unchanged if already sequential.
        - Every time 'Cyc-Count' resets, 'abs_cycle' increments once.
        """
        if "Cyc-Count" not in dataset.columns:
            messagebox.showerror("Error", "Dataset is missing the 'Cyc-Count' column.")
            return dataset  # Return original dataset to avoid breaking functionality

        cyc_count = dataset["Cyc-Count"].tolist()  # Extract as a list
        expected_cycle = 1
        last_cycle = 1
        abs_cycle = []

        for cyc in cyc_count:
            if cyc == expected_cycle:
                abs_cycle.append(expected_cycle)
            else:
                if cyc != last_cycle:
                    expected_cycle += 1
                    abs_cycle.append(expected_cycle)
                else:
                    abs_cycle.append(expected_cycle)
            last_cycle = cyc

        dataset["abs_cycle"] = abs_cycle  # Add the computed column to the dataset
        return dataset

    def modify_dataset(self, dataset_type):
        """
        Apply modifications to the dataset and store it.
        """
        data = self.datasets.get(dataset_type, {}).get("data")
        if data is None:
            messagebox.showerror("Error", f"No {dataset_type} dataset loaded.")
            return

        modified_data = data.copy()

        widget = self.anode_modify_widget if dataset_type == "anode" else self.cathode_modify_widget

        if widget.compute_du_dq.get():
            if "Ah-Cyc-Discharge-0" in modified_data.columns and "U[V]" in modified_data.columns:
                modified_data["dU/dQ"] = np.gradient(modified_data["U[V]"], modified_data["Ah-Cyc-Discharge-0"])

        if widget.normalize_voltage.get():
            if "U[V]" in modified_data.columns:
                max_voltage = modified_data["U[V]"].max()
                modified_data["U_normalized"] = modified_data["U[V]"] / max_voltage

        # Store the latest modified dataset instead of appending to a list
        self.modified_datasets[dataset_type] = modified_data

        messagebox.showinfo("Success", f"Modified dataset stored for {dataset_type}.")

    def _show_modified_data(self, dataset_type):
        """
        Display the modified dataset in a new window.
        """
        dataset = self.modified_datasets.get(dataset_type)
        if dataset is None:
            messagebox.showerror("Error", f"No modified {dataset_type} dataset available.")
            return

        table_window = tk.Toplevel(self.root)
        table_window.title(f"Modified Data - {dataset_type.capitalize()}")
        table_window.geometry("800x600")

        x_scrollbar = tk.Scrollbar(table_window, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")

        y_scrollbar = tk.Scrollbar(table_window, orient="vertical")
        y_scrollbar.pack(side="right", fill="y")

        text = tk.Text(table_window, wrap="none", xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
        text.pack(side="left", fill="both", expand=True)

        x_scrollbar.config(command=text.xview)
        y_scrollbar.config(command=text.yview)

        text.insert("1.0", dataset.to_string(index=False))

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
        anode_spline = self.compute_linear_spline(anode_discharge["Ah-Cyc-Discharge-0"], anode_discharge["U[V]"])
        cathode_spline = self.compute_linear_spline(cathode_charge["Ah-Cyc-Charge-0"], cathode_charge["U[V]"])

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
        self.filtered_datasets.setdefault("full_cell", []).append({"name": dataset_name, "data": full_cell_data})
        self.full_cell_browser.add_dataset(dataset_name)  # Add to full cell browser

        messagebox.showinfo("Success", f"Full cell dataset created: {dataset_name}")

    def _get_dataset_by_name(self, dataset_name, dataset_type):
        """
        Retrieve the dataset by name from the stored filtered datasets.
        """
        datasets = self.filtered_datasets.get(dataset_type, [])
        for dataset in datasets:
            if dataset["name"] == dataset_name:
                return dataset["data"]
        return None

    def _plot_multi_graph(self):
        plotter = MultiGraphPlotter(self)
        plotter.plot_multi_graph()


    def show_data_table(self, dataset_type):
        """
        Displays the selected dataset (anode or cathode) in a new window.
        """
        data = self.datasets.get(dataset_type, {}).get("data")
        if data is None:
            messagebox.showerror("Error", f"No {dataset_type} dataset loaded.")
            return

        # Create a new window for the data table
        table_window = tk.Toplevel(self.root)
        table_window.title(f"Data Table - {dataset_type.capitalize()}")
        table_window.geometry("800x600")

        # Add scrollbars
        x_scrollbar = tk.Scrollbar(table_window, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")

        y_scrollbar = tk.Scrollbar(table_window, orient="vertical")
        y_scrollbar.pack(side="right", fill="y")

        # Create a Text widget to display the data
        text = tk.Text(table_window, wrap="none", xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
        text.pack(side="left", fill="both", expand=True)

        # Configure the scrollbars
        x_scrollbar.config(command=text.xview)
        y_scrollbar.config(command=text.yview)

        # Insert the data into the Text widget
        text.insert("1.0", data.to_string(index=False))
        
    def plot_data(self, dataset_type):
        """
        Plots the selected dataset (anode or cathode).
        """
        data = self.datasets.get(dataset_type, {}).get("data")
        if data is None:
            messagebox.showerror("Error", f"No {dataset_type} dataset loaded.")
            return

        try:
            plt.figure(figsize=(8, 6))
            plt.plot(data["Time[h]"], data["U[V]"], label=f"{dataset_type.capitalize()} Voltage")
            plt.xlabel("Time (h)")
            plt.ylabel("Voltage (V)")
            plt.title(f"{dataset_type.capitalize()} Data Plot")
            plt.legend()
            plt.grid(True)
            plt.show()
        except KeyError as e:
            messagebox.showerror("Error", f"Missing column in data: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def apply_filters(self, dataset_type):
        """
        Applies selected filters and modifications to the given dataset.
        """
        data = self.datasets.get(dataset_type, {}).get("data")
        if data is None:
            messagebox.showerror("Error", f"No {dataset_type} dataset loaded.")
            return None

        # Apply filters first
        filtered_data = data.copy()
        widget = self.anode_filter_widget if dataset_type == "anode" else self.cathode_filter_widget
        modify_widget = self.anode_modify_widget if dataset_type == "anode" else self.cathode_modify_widget

        if widget.remove_pause.get():
            filtered_data = filtered_data[filtered_data['Command'] != 'Pause']

        if widget.select_cycle.get():
            selected_cycle = widget.cycle_selection.get()
            if selected_cycle and selected_cycle != "All":
                filtered_data = filtered_data[filtered_data['Cyc-Count'] == int(selected_cycle)]

        if widget.select_charge_half_cycle.get():
            filtered_data = filtered_data[filtered_data['Command'].str.contains("Charge", na=False)]

        if widget.select_discharge_half_cycle.get():
            filtered_data = filtered_data[filtered_data['Command'].str.contains("Discharge", na=False)]

        # Step Change Filtering
        if widget.apply_step_change.get():
            step_column = widget.step_change_column.get()
            if step_column in filtered_data.columns:
                filtered_data = self.step_change_filter(filtered_data, step_column)
            else:
                messagebox.showerror("Error", f"Column '{step_column}' not found in dataset.")

        if filtered_data.empty:
            messagebox.showerror("Error", f"No data available after filtering {dataset_type}.")
            return None

        # ✅ Apply modifications with the corrected compute_absolute_cycle function
        if modify_widget.compute_abs_cycle.get():
            filtered_data = self.compute_absolute_cycle(filtered_data)

        if modify_widget.compute_du_dq.get():
            if "Ah-Cyc-Charge-0" in filtered_data.columns and "U[V]" in filtered_data.columns:
                filtered_data["dU/dQ"] = (
                    filtered_data["U[V]"].diff() / filtered_data["Ah-Cyc-Charge-0"].diff()
                )

        if modify_widget.normalize_voltage.get():
            if "U[V]" in filtered_data.columns:
                max_voltage = filtered_data["U[V]"].max()
                filtered_data["U_normalized"] = filtered_data["U[V]"] / max_voltage

        return filtered_data  # ✅ Return cleaned-up modified dataset

    def plot_filtered_data(self, dataset_type):
        """
        Plots the filtered data for the selected dataset type, supporting:
        - 'Show Cycles' with an option to use 'Cyc-Count' or 'abs_cycle'
        - 'Linear Spline'
        - 'Show Key Values'
        """
        filtered_data = self.apply_filters(dataset_type)
        if filtered_data is None:
            return

        # Get the filter and key value widgets for the dataset
        filter_widget = (
            self.anode_filter_widget if dataset_type == "anode" else self.cathode_filter_widget
        )
        key_values_widget = (
            self.anode_key_values_widget if dataset_type == "anode" else self.cathode_key_values_widget
        )

        plot_type = filter_widget.plot_option.get()
        show_cycles = filter_widget.show_cycles.get()
        fit_type = filter_widget.fit_option.get()
        show_key_values = filter_widget.visualize_key_values.get()

        # Get the cycle column selection from the dropdown (default: Cyc-Count)
        cycle_column = filter_widget.cycle_column_option.get()  # "Cyc-Count" or "abs_cycle"

        try:
            plt.figure(figsize=(8, 6))

            # Determine x, y columns based on the plot type
            if plot_type == "U-t":
                x = filtered_data["Time[h]"]
                y = filtered_data["U[V]"]
                xlabel, ylabel, title = "Time (h)", "Voltage (V)", f"{dataset_type.capitalize()} Data: U vs t"

            elif plot_type == "I-t":
                x = filtered_data["Time[h]"]
                y = filtered_data["I[A]"]
                xlabel, ylabel, title = "Time (h)", "Current (A)", f"{dataset_type.capitalize()} Data: I vs t"

            elif plot_type == "Q-U":
                charge_column = (
                    "Ah-Cyc-Discharge-0"
                    if filter_widget.select_discharge_half_cycle.get()
                    else "Ah-Cyc-Charge-0"
                )
                if charge_column not in filtered_data.columns:
                    messagebox.showerror("Error", f"Column '{charge_column}' not found in dataset.")
                    return
                x = filtered_data[charge_column]
                y = filtered_data["U[V]"]
                xlabel, ylabel, title = "Charge (Ah)", "Voltage (V)", f"{dataset_type.capitalize()} Data: Q vs U"

            else:
                messagebox.showerror("Error", "Invalid plot type selected.")
                return

            # Show Cycles functionality with cycle column selection
            if show_cycles:
                if cycle_column not in filtered_data.columns:
                    messagebox.showerror("Error", f"Selected cycle column '{cycle_column}' is missing in the dataset.")
                    return

                cycle_groups = filtered_data.groupby(cycle_column)
                colors = plt.cm.tab10.colors  # Use a colormap for cycles
                for i, (cycle, group) in enumerate(cycle_groups):
                    plt.plot(group[x.name], group[y.name], label=f"Cycle {cycle}", color=colors[i % len(colors)])
            else:
                # Default plot (no cycle grouping)
                plt.plot(x, y, label="Filtered Data")

            # Linear Spline functionality (if enabled)
            if fit_type == "linear spline":
                spline_data = self.compute_linear_spline(x, y)
                if spline_data:
                    plt.plot(
                        spline_data["x"], spline_data["y"], label="Linear Spline Fit", color="red", linestyle="--"
                    )

            # Show Key Values functionality (if enabled)
            if show_key_values:
                key_points = self.compute_key_points(filtered_data, filter_widget, key_values_widget, plot_type)
                for point in key_points:
                    plt.scatter(point["x"], point["y"], color=point["color"], marker=point["marker"], s=100)
                    plt.text(
                        point["x"], point["y"], point["label"], color=point["color"], fontsize=10, ha="right", va="bottom"
                    )

            # Add labels, title, grid, and legend
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.title(title)
            plt.legend()
            plt.grid(True)
            plt.show()

        except KeyError as e:
            messagebox.showerror("Error", f"Missing column in data: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def _generate_filter_suffix(self, dataset_type):
        """
        Generate a suffix string based on the applied filters.
        """
        widget = self.anode_filter_widget if dataset_type == "anode" else self.cathode_filter_widget
        suffixes = []

        if widget.remove_pause.get():
            suffixes.append("nopause")
        if widget.select_cycle.get():
            # Use the selected cycle from the dropdown
            selected_cycle = widget.cycle_selection.get()
            if selected_cycle and selected_cycle != "All":
                suffixes.append(f"cycle{selected_cycle}")
            else:
                suffixes.append("allcycles")
        if widget.select_charge_half_cycle.get():
            suffixes.append("charge")
        if widget.select_discharge_half_cycle.get():
            suffixes.append("discharge")
        if widget.apply_step_change.get():
            suffixes.append("sc")  # Step Change filter suffix

        return "-".join(suffixes) if suffixes else "nofilter"

    def store_filtered_data(self, dataset_type):
        """
        Store the filtered dataset in the respective browser.
        """
        if self.datasets[dataset_type]["data"] is None:
            messagebox.showerror("Error", f"No {dataset_type} data loaded.")
            return

        # Apply filters to the dataset
        filtered_data = self.apply_filters(dataset_type)
        if filtered_data is None or filtered_data.empty:
            messagebox.showerror("Error", f"No data available after filtering {dataset_type}.")
            return

        # Generate dataset name with filters
        dataset_file = self.datasets[dataset_type]["file_path"].get()
        if dataset_file == "No file selected":
            dataset_file = "Unknown"
        filter_suffix = self._generate_filter_suffix(dataset_type)
        dataset_name = f"{os.path.splitext(dataset_file)[0]}_{filter_suffix}"

        # Store the dataset in internal storage and the respective browser
        self.filtered_datasets[dataset_type].append({"name": dataset_name, "data": filtered_data})
        if dataset_type == "anode":
            self.anode_browser.add_dataset(dataset_name)
        else:
            self.cathode_browser.add_dataset(dataset_name)

        messagebox.showinfo("Success", f"Filtered dataset stored: {dataset_name}")


    def compute_linear_spline(self, x, y):
        """
        Computes linear spline fit for given x and y data.
        Returns a dictionary with x and y values for the spline.
        """
        try:
            from scipy.interpolate import interp1d

            spline = interp1d(x, y, kind="linear", fill_value="extrapolate")
            x_fit = np.linspace(x.min(), x.max(), 500)  # Generate 500 evenly spaced points for smoothness
            y_fit = spline(x_fit)

            return {"x": x_fit, "y": y_fit}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compute linear spline: {e}")
            return None

    def compute_key_values(self, dataset_type):
        """
        Computes key values (max voltage, max charge, max discharge) for the filtered dataset.
        Returns a dictionary of results.
        """
        filtered_data = self.apply_filters(dataset_type)
        if filtered_data is None:
            return None

        # Get the widget for the dataset
        widget = self.anode_key_values_widget if dataset_type == "anode" else self.cathode_key_values_widget

        # Prepare results
        results = {"Cycle": []}
        if widget.extract_max_voltage.get():
            results["Max Voltage (V)"] = []
        if widget.extract_max_charge.get():
            results["Max Charge (Ah)"] = []
        if widget.extract_max_discharge.get():
            results["Max Discharge (Ah)"] = []

        # Group data by cycle if Cyc-Count column exists
        grouped_data = filtered_data.groupby("Cyc-Count") if "Cyc-Count" in filtered_data.columns else [("", filtered_data)]

        for cycle, group in grouped_data:
            results["Cycle"].append(cycle)

            if widget.extract_max_voltage.get():
                results["Max Voltage (V)"].append(group["U[V]"].max())

            if widget.extract_max_charge.get():
                if "Ah-Cyc-Charge-0" in group.columns:
                    results["Max Charge (Ah)"].append(group["Ah-Cyc-Charge-0"].max())
                else:
                    results["Max Charge (Ah)"].append("N/A")

            if widget.extract_max_discharge.get():
                if "Ah-Cyc-Discharge-0" in group.columns:
                    results["Max Discharge (Ah)"].append(group["Ah-Cyc-Discharge-0"].max())
                else:
                    results["Max Discharge (Ah)"].append("N/A")

        return results

    def show_key_values_table(self, results, dataset_type):
        """
        Displays the computed key values in a new window.
        """
        if results is None:
            messagebox.showerror("Error", f"Failed to compute key values for {dataset_type}.")
            return

        # Create a new window for the results
        results_window = tk.Toplevel(self.root)
        results_window.title(f"Key Values - {dataset_type.capitalize()}")
        results_window.geometry("600x400")

        # Add scrollbars
        x_scrollbar = tk.Scrollbar(results_window, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")

        y_scrollbar = tk.Scrollbar(results_window, orient="vertical")
        y_scrollbar.pack(side="right", fill="y")

        # Create a Text widget to display the data
        text = tk.Text(results_window, wrap="none", xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
        text.pack(side="left", fill="both", expand=True)

        # Configure the scrollbars
        x_scrollbar.config(command=text.xview)
        y_scrollbar.config(command=text.yview)

        # Insert the results into the Text widget
        import pandas as pd
        results_df = pd.DataFrame(results)
        text.insert("1.0", results_df.to_string(index=False))

    def extract_key_values(self, dataset_type):
        """
        Extracts and displays key values for the selected dataset type.
        """
        results = self.compute_key_values(dataset_type)
        self.show_key_values_table(results, dataset_type)

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
