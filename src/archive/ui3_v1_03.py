import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class FilteredDataBrowser:
    """
    A widget for displaying and managing filtered datasets.
    """

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

    def add_dataset(self, dataset_name):
        """
        Add a dataset to the browser.
        """
        self.listbox.insert(tk.END, dataset_name)

    def get_selected_datasets(self):
        """
        Get the selected datasets from the browser.
        """
        selected_indices = self.listbox.curselection()
        return [self.listbox.get(i) for i in selected_indices]

    def clear_browser(self):
        """
        Clear all datasets from the browser.
        """
        self.listbox.delete(0, tk.END)


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
        self.plot_option = tk.StringVar(value="U-t")
        self.fit_option = tk.StringVar(value="no fit")
        self.visualize_key_values = tk.BooleanVar(value=False)
        self.show_cycles = tk.BooleanVar(value=False)

        self._create_filter_options()

        # Add Plot and Save Buttons
        tk.Button(self.frame, text="Plot Filtered Data", command=self._plot_filtered_data).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        tk.Button(self.frame, text="Save Filtered Data", command=self._save_filtered_data).grid(row=1, column=1, padx=10, pady=5, sticky="w")
        # Add a "Store Filtered Data" button in FilterWidget
        tk.Button(self.frame, text="Store Filtered Data", command=self._store_filtered_data).grid(row=1, column=2, padx=10, pady=5, sticky="w")


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
        self.filtered_datasets = {"anode": [], "cathode": []}

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

        self.anode_filter_widget = FilterWidget(filter_section, "Filter Anode Data", "anode", self)
        self.cathode_filter_widget = FilterWidget(filter_section, "Filter Cathode Data", "cathode", self)

        # Key Values Sections
        key_values_section = tk.Frame(self.main_frame)
        key_values_section.pack(fill="x")
        key_values_section.grid_columnconfigure(0, weight=1)
        key_values_section.grid_columnconfigure(1, weight=1)

        self.anode_key_values_widget = KeyValuesWidget(key_values_section, "Extract Anode Key Values", "anode", self)
        self.cathode_key_values_widget = KeyValuesWidget(key_values_section, "Extract Cathode Key Values", "cathode", self)

        # Filtered Data Browsers
        browser_section = tk.Frame(self.main_frame)
        browser_section.pack(fill="x")
        browser_section.grid_columnconfigure(0, weight=1)
        browser_section.grid_columnconfigure(1, weight=1)

        self.anode_browser = FilteredDataBrowser(browser_section, "Filtered Anode Data Browser", "anode", self)
        self.cathode_browser = FilteredDataBrowser(browser_section, "Filtered Cathode Data Browser", "cathode", self)

        # Full Cell Data Section
        tk.Label(self.main_frame, text="Full cell data section", font=("Arial", 12, "underline")).pack(pady=5)
        tk.Button(self.main_frame, text="Plot Prediction", command=self._plot_full_cell_prediction).pack(pady=10)

    def select_file(self, dataset_type):
        """
        Allows the user to select a file and updates the dataset.
        """
        initial_dir = os.path.join(os.getcwd(), "data")  # Default to /data subfolder
        file_path = filedialog.askopenfilename(
            title=f"Select {dataset_type.capitalize()} Data File",
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*.*")],
            initialdir=initial_dir,
        )
        if file_path:
            try:
                # Load dataset
                data = pd.read_csv(file_path, skiprows=12, delimiter=",", encoding="utf-8", on_bad_lines="skip")
                self.datasets[dataset_type]["data"] = data
                self.datasets[dataset_type]["file_path"].set(os.path.basename(file_path))  # Update file name
                messagebox.showinfo("Success", f"{dataset_type.capitalize()} dataset loaded.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load {dataset_type} dataset: {e}")

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
        Applies selected filters to the given dataset.
        """
        data = self.datasets.get(dataset_type, {}).get("data")
        if data is None:
            messagebox.showerror("Error", f"No {dataset_type} dataset loaded.")
            return None

        filtered_data = data.copy()

        # Get the filter options from the widget
        widget = self.anode_filter_widget if dataset_type == "anode" else self.cathode_filter_widget

        if widget.remove_pause.get():
            filtered_data = filtered_data[filtered_data['Command'] != 'Pause']

        if widget.select_cycle.get():
            cycle_number = tk.simpledialog.askinteger("Cycle Selection", "Enter Cycle Number:")
            if cycle_number is not None:
                filtered_data = filtered_data[filtered_data['Cyc-Count'] == cycle_number]

        if widget.select_charge_half_cycle.get():
            filtered_data = filtered_data[filtered_data['Command'].str.contains("Charge", na=False)]

        if widget.select_discharge_half_cycle.get():
            filtered_data = filtered_data[filtered_data['Command'].str.contains("Discharge", na=False)]

        if filtered_data.empty:
            messagebox.showerror("Error", f"No data available after applying filters to {dataset_type}.")
            return None

        return filtered_data

    def plot_filtered_data(self, dataset_type):
        """
        Plots the filtered data for the selected dataset type, supporting 'Show Cycles',
        'Linear Spline', and 'Show Key Values'.
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

            # Show Cycles functionality (if enabled)
            if show_cycles and "Cyc-Count" in filtered_data.columns:
                cycle_groups = filtered_data.groupby("Cyc-Count")
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
    '''
        def _generate_filter_suffix(self, dataset_type):
            """
            Generate a suffix string based on the applied filters.
            """
            widget = self.anode_filter_widget if dataset_type == "anode" else self.cathode_filter_widget
            suffixes = []

            if widget.remove_pause.get():
                suffixes.append("nopause")
            if widget.select_cycle.get():
                # Ask for the selected cycle number and include it in the suffix
                cycle_number = tk.simpledialog.askinteger("Cycle Selection", "Enter Cycle Number:")
                if cycle_number is not None:
                    suffixes.append(f"cycle{cycle_number}")
                else:
                    suffixes.append("cycle")  # Fallback if no cycle number is provided
            if widget.select_charge_half_cycle.get():
                suffixes.append("charge")
            if widget.select_discharge_half_cycle.get():
                suffixes.append("discharge")

            return "-".join(suffixes) if suffixes else "nofilter"

    '''
    def _generate_filter_suffix(self, dataset_type, cycle_number=None):
        """
        Generate a suffix string based on the applied filters.
        """
        widget = self.anode_filter_widget if dataset_type == "anode" else self.cathode_filter_widget
        suffixes = []

        if widget.remove_pause.get():
            suffixes.append("nopause")
        if widget.select_cycle.get():
            # Use the provided cycle_number or prompt the user if not already provided
            if cycle_number is None:
                cycle_number = tk.simpledialog.askinteger("Cycle Selection", "Enter Cycle Number:")
            if cycle_number is not None:
                suffixes.append(f"cycle{cycle_number}")
            else:
                suffixes.append("cycle")  # Fallback if no cycle number is provided
        if widget.select_charge_half_cycle.get():
            suffixes.append("charge")
        if widget.select_discharge_half_cycle.get():
            suffixes.append("discharge")

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

    def save_filtered_data(self, dataset_type):
        """
        Saves the filtered data to a user-specified file, with suffixes describing applied filters.
        """
        filtered_data = self.apply_filters(dataset_type)
        if filtered_data is None:
            return

        # Suggest a base filename
        dataset_file = self.datasets[dataset_type]["file_path"].get()
        if dataset_file == "No file selected":
            messagebox.showerror("Error", f"No {dataset_type} file loaded.")
            return

        base_filename = os.path.splitext(os.path.basename(dataset_file))[0]
        filter_suffix = self._generate_filter_suffix(dataset_type)
        suggested_filename = f"{base_filename}_{filter_suffix}_filtered.csv"

        # Set the default directory to "filtered_data"
        save_folder = os.path.join(os.getcwd(), "filtered_data")
        os.makedirs(save_folder, exist_ok=True)

        # Open file dialog starting in "filtered_data" with the proposed filename
        save_path = filedialog.asksaveasfilename(
            title="Save Filtered Data",
            initialdir=save_folder,
            initialfile=suggested_filename,
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if save_path:
            try:
                filtered_data.to_csv(save_path, index=False)
                messagebox.showinfo("Success", f"Filtered data saved to {save_path}.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save filtered data: {e}")

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


    # Reuse existing methods like select_file, show_data_table, etc.

    def _plot_full_cell_prediction(self):
            # TODO: Implement full cell prediction logic
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = HC2FCApp(root)
    root.mainloop()
