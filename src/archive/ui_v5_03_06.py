import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class HC2FCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("hc2fc")
        self.root.geometry("800x600")

        # Initialize datasets dictionary
        self.datasets = {
            "anode": {"data": None, "file_path": tk.StringVar(value="No file selected")},
            "cathode": {"data": None, "file_path": tk.StringVar(value="No file selected")},
        }
        self.current_dataset_type = tk.StringVar(value="No dataset selected")
        self.selected_filter_dataset = tk.StringVar(value="anode")  # Default to "anode"
        self.show_cycles = tk.BooleanVar(value=False)  # Default: Do not show cycles



        # Main container frame with scrollbar
        container = tk.Frame(root)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container)
        self.scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame inside the canvas
        self.main_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        self.main_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Title
        tk.Label(self.main_frame, text="hc2fc", font=("Arial", 16, "bold")).pack(pady=10)

        # Add sections
        self.add_sections()


    def add_sections(self):
        # Half Cell Data Section
        tk.Label(self.main_frame, text="Half cell data", font=("Arial", 12, "underline")).pack(pady=5)
        self.create_half_cell_section(self.main_frame)

        # Filter Half Cell Data Section
        tk.Label(self.main_frame, text="Filter half cell data", font=("Arial", 12, "underline")).pack(pady=5)
        self.create_filter_section(self.main_frame)

        # Extract Key Values Section
        tk.Label(self.main_frame, text="Extract Key Values", font=("Arial", 12, "underline")).pack(pady=5)
        self.create_extract_key_values_section(self.main_frame)

    def create_half_cell_section(self, parent):
        frame = tk.Frame(parent, relief="groove", borderwidth=2)
        frame.pack(pady=10, padx=20, fill="x", expand=False)

        # Anode
        tk.Label(frame, text="Anode file:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Label(frame, textvariable=self.datasets["anode"]["file_path"], width=40, anchor="w").grid(
            row=0, column=1, sticky="ew", padx=5, pady=5
        )
        tk.Button(frame, text="Load", command=lambda: self.select_file("anode")).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(frame, text="Show Data Table", command=lambda: self.show_data_table("anode")).grid(row=0, column=3, padx=5, pady=5)
        tk.Button(frame, text="Plot Data", command=lambda: self.plot_data("anode")).grid(row=0, column=4, padx=5, pady=5)

        # Cathode
        tk.Label(frame, text="Cathode file:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Label(frame, textvariable=self.datasets["cathode"]["file_path"], width=40, anchor="w").grid(
            row=1, column=1, sticky="ew", padx=5, pady=5
        )
        tk.Button(frame, text="Load", command=lambda: self.select_file("cathode")).grid(row=1, column=2, padx=5, pady=5)
        tk.Button(frame, text="Show Data Table", command=lambda: self.show_data_table("cathode")).grid(row=1, column=3, padx=5, pady=5)
        tk.Button(frame, text="Plot Data", command=lambda: self.plot_data("cathode")).grid(row=1, column=4, padx=5, pady=5)

        # Current Dataset
        tk.Label(frame, text="Currently loaded:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Label(frame, textvariable=self.current_dataset_type, fg="red").grid(row=2, column=1, sticky="w", padx=5, pady=5)

        frame.grid_columnconfigure(1, weight=1)



    def create_filter_section(self, parent):
        frame = tk.Frame(parent, relief="groove", borderwidth=2)
        frame.pack(pady=10, padx=20, fill="x", expand=False)

        # Dataset Selection
        dataset_frame = tk.LabelFrame(frame, text="Select Dataset", font=("Arial", 10))
        dataset_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        self.filter_dataset_selection = tk.StringVar(value="anode")  # Default to "anode"
        self.selected_filter_dataset = self.filter_dataset_selection  # Bind filter selection to the app variable
        tk.Radiobutton(dataset_frame, text="Anode", variable=self.filter_dataset_selection, value="anode").pack(anchor="w", padx=5, pady=2)
        tk.Radiobutton(dataset_frame, text="Cathode", variable=self.filter_dataset_selection, value="cathode").pack(anchor="w", padx=5, pady=2)

        # Filter Criteria Selection
        filter_frame = tk.LabelFrame(frame, text="Select filter criteria", font=("Arial", 10))
        filter_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        self.remove_pause = tk.BooleanVar()
        self.select_cycle = tk.BooleanVar()
        self.select_charge_half_cycle = tk.BooleanVar()
        self.select_discharge_half_cycle = tk.BooleanVar()

        tk.Checkbutton(filter_frame, text="Remove pause", variable=self.remove_pause).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        tk.Checkbutton(filter_frame, text="Select cycle", variable=self.select_cycle).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        tk.Checkbutton(filter_frame, text="Select charge half cycle", variable=self.select_charge_half_cycle).grid(row=2, column=0, sticky="w", padx=5, pady=2)
        tk.Checkbutton(filter_frame, text="Select discharge half cycle", variable=self.select_discharge_half_cycle).grid(row=3, column=0, sticky="w", padx=5, pady=2)

        # Plot Type Selection
        plot_options_frame = tk.LabelFrame(frame, text="Select plot type", font=("Arial", 10))
        plot_options_frame.grid(row=2, column=0, rowspan=4, padx=5, pady=5, sticky="nsew")
        self.filter_plot_option = tk.StringVar(value="U-t")  # Default plot option
        tk.Radiobutton(plot_options_frame, text="U vs t (Voltage-Time)", variable=self.filter_plot_option, value="U-t").pack(anchor="w", padx=5)
        tk.Radiobutton(plot_options_frame, text="I vs t (Current-Time)", variable=self.filter_plot_option, value="I-t").pack(anchor="w", padx=5)
        tk.Radiobutton(plot_options_frame, text="Q vs U (Charge-Voltage)", variable=self.filter_plot_option, value="Q-U").pack(anchor="w", padx=5)

        # Fit Type Selection
        fit_options_frame = tk.LabelFrame(frame, text="Select fit type", font=("Arial", 10))
        fit_options_frame.grid(row=2, column=2, rowspan=4, padx=5, pady=5, sticky="nsew")
        self.filter_fit_option = tk.StringVar(value="no fit")  # Default fit option
        tk.Radiobutton(fit_options_frame, text="No Fit", variable=self.filter_fit_option, value="no fit").pack(anchor="w", padx=5)
        tk.Radiobutton(fit_options_frame, text="Linear Spline", variable=self.filter_fit_option, value="linear spline").pack(anchor="w", padx=5)

        # Visualization Type Selection
        visualization_frame = tk.LabelFrame(frame, text="Select visualization type", font=("Arial", 10))
        visualization_frame.grid(row=2, column=4, rowspan=4, padx=5, pady=5, sticky="nsew")
        self.visualize_key_values = tk.BooleanVar(value=False)
        tk.Checkbutton(visualization_frame, text="Show Key Values", variable=self.visualize_key_values).pack(anchor="w", padx=5)
        tk.Checkbutton(visualization_frame, text="Show Cycles", variable=self.show_cycles).pack(anchor="w", padx=5)


        # Buttons for actions
        tk.Button(frame, text="Plot filtered data", command=self.plot_filtered_data).grid(row=3, column=5, padx=10, pady=5)
        tk.Button(frame, text="Save filtered data", command=self.save_filtered_data).grid(row=4, column=5, padx=10, pady=5)

        # Adjust column weights for resizing
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)
        frame.grid_columnconfigure(3, weight=1)
        frame.grid_columnconfigure(4, weight=1)
        frame.grid_columnconfigure(5, weight=1)


    def create_extract_key_values_section(self, parent):
        frame = tk.Frame(parent, relief="groove", borderwidth=2)
        frame.pack(pady=10, padx=20, fill="x", expand=False)

        # Title
        tk.Label(frame, text="Extract Key Values", font=("Arial", 12, "underline")).grid(row=0, column=0, columnspan=3, pady=5, sticky="w")

        # Key Value Checkboxes
        self.extract_max_voltage = tk.BooleanVar()
        self.extract_max_charge = tk.BooleanVar()
        self.extract_max_discharge = tk.BooleanVar()

        tk.Checkbutton(frame, text="Max Voltage", variable=self.extract_max_voltage).grid(row=1, column=0, sticky="w", padx=5)
        tk.Checkbutton(frame, text="Max Ah-Cyc-Charge-0", variable=self.extract_max_charge).grid(row=2, column=0, sticky="w", padx=5)
        tk.Checkbutton(frame, text="Max Ah-Cyc-Discharge-0", variable=self.extract_max_discharge).grid(row=3, column=0, sticky="w", padx=5)

        # Button to extract and display values
        tk.Button(frame, text="Extract Key Values", command=self.extract_key_values).grid(row=4, column=0, columnspan=2, padx=10, pady=5)


    '''
    def select_file(self, dataset_type):
        """
        Allows the user to select a file and updates the dataset.
        """
        # Get the absolute path to the "data" directory relative to the script's location
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, "data")

        file_path = filedialog.askopenfilename(
            title=f"Select {dataset_type.capitalize()} Data File",
            initialdir=data_dir,  # Set the initial directory to the "data" subdirectory
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                # Load dataset
                data = self.load_dataset(file_path)
                self.datasets[dataset_type]["data"] = data
                self.datasets[dataset_type]["file_path"] = file_path  # Update StringVar
                self.current_dataset_type.set(f"{dataset_type.capitalize()} Dataset Loaded")
                messagebox.showinfo("Success", f"{dataset_type.capitalize()} dataset loaded.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load {dataset_type} dataset: {e}")
    '''

    def select_file(self, dataset_type):
        """
        Allows the user to select a file and updates the dataset.
        """
        initial_dir = os.path.join(os.getcwd(), "data")  # Ensure starting in the /data subfolder
        file_path = filedialog.askopenfilename(
            title=f"Select {dataset_type.capitalize()} Data File",
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*.*")],
            initialdir=initial_dir,
        )
        if file_path:
            try:
                # Load dataset
                data = self.load_dataset(file_path)
                self.datasets[dataset_type]["data"] = data
                self.datasets[dataset_type]["file_path"].set(os.path.basename(file_path))  # Update display with file name
                self.current_dataset_type.set(f"{dataset_type.capitalize()} Dataset Loaded")
                messagebox.showinfo("Success", f"{dataset_type.capitalize()} dataset loaded.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load {dataset_type} dataset: {e}")



    def load_dataset(self, file_path):
        """
        Loads a dataset from the specified file path.
        """
        return pd.read_csv(file_path, skiprows=12, delimiter=",", encoding="utf-8", on_bad_lines="skip")

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

        plt.figure(figsize=(8, 6))
        plt.plot(data["Time[h]"], data["U[V]"], label=f"{dataset_type.capitalize()} Voltage")
        plt.xlabel("Time (h)")
        plt.ylabel("Voltage (V)")
        plt.title(f"{dataset_type.capitalize()} Data Plot")
        plt.legend()
        plt.grid(True)
        plt.show()


    def select_cycle(self):
        """
        Allows the user to select a specific cycle for further analysis.
        """
        if not hasattr(self, 'cycle_data'):
            messagebox.showerror("Error", "Data has not been split by cycle. Please split the data first.")
            return

        # Create a simple prompt to select a cycle (can be replaced with a dropdown in the future)
        cycle_numbers = list(self.cycle_data.groups.keys())
        selected_cycle = tk.simpledialog.askinteger("Select Cycle", f"Available cycles: {cycle_numbers}\nEnter a cycle number:")

        if selected_cycle in cycle_numbers:
            self.selected_cycle_data = self.cycle_data.get_group(selected_cycle)
            messagebox.showinfo("Success", f"Cycle {selected_cycle} selected for analysis.")
        else:
            messagebox.showerror("Error", "Invalid cycle number selected.")

    def plot_data_split(self):
        """
        Plots all the data splits (grouped by cycles) on a single graph for comparison.
        """
        if not hasattr(self, 'cycle_data'):
            messagebox.showerror("Error", "Data has not been split by cycle. Please split the data first.")
            return

        try:
            plt.figure(figsize=(8, 6))
            for cycle, data in self.cycle_data:
                plt.plot(data['Time[h]'], data['U[V]'], label=f"Cycle {cycle}")

            plt.xlabel("Time (h)")
            plt.ylabel("Voltage (V)")
            plt.title("Data Split by Cycles")
            plt.legend()
            plt.grid(True)
            plt.show()
        except KeyError as e:
            messagebox.showerror("Error", f"Column not found: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def plot_cycle(self):
        """
        Plots the selected cycle data.
        """
        if not hasattr(self, 'selected_cycle_data'):
            messagebox.showerror("Error", "No cycle selected. Please select a cycle first.")
            return

        try:
            plt.figure(figsize=(8, 6))
            plt.plot(self.selected_cycle_data['Time[h]'], self.selected_cycle_data['U[V]'], label="Selected Cycle")
            plt.xlabel("Time (h)")
            plt.ylabel("Voltage (V)")
            plt.title("Plot of Selected Cycle")
            plt.legend()
            plt.grid(True)
            plt.show()
        except KeyError as e:
            messagebox.showerror("Error", f"Column not found: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def plot_filtered_data(self):
        """
        Plots the filtered data and optionally the fit data, highlighting key values if selected.
        Also supports visualizing cycles with distinct colors.
        """
        # Synchronize dataset selection
        self.selected_filter_dataset.set(self.filter_dataset_selection.get())

        filtered_data, fit_data = self.apply_filters()
        if filtered_data is None:
            return  # Exit if filtering failed

        # Determine the selected plot type
        plot_type = self.filter_plot_option.get()
        try:
            plt.figure(figsize=(8, 6))

            if plot_type == "U-t":
                if self.show_cycles.get() and "Cyc-Count" in filtered_data.columns:
                    # Group by cycle and assign colors
                    cycle_groups = filtered_data.groupby("Cyc-Count")
                    colors = plt.cm.tab10.colors  # Use a colormap
                    for i, (cycle, group) in enumerate(cycle_groups):
                        color = colors[i % len(colors)]
                        plt.plot(group["Time[h]"], group["U[V]"], label=f"Cycle {cycle}", color=color)
                else:
                    plt.plot(filtered_data["Time[h]"], filtered_data["U[V]"], label="Filtered Data (Voltage-Time)")

                plt.xlabel("Time (h)")
                plt.ylabel("Voltage (V)")
                plt.title("Filtered Data: U vs t")

            elif plot_type == "I-t":
                plt.plot(filtered_data["Time[h]"], filtered_data["I[A]"], label="Filtered Data (Current-Time)", color="orange")
                plt.xlabel("Time (h)")
                plt.ylabel("Current (A)")
                plt.title("Filtered Data: I vs t")

            elif plot_type == "Q-U":
                x = (
                    filtered_data["Ah-Cyc-Discharge-0"]
                    if self.select_discharge_half_cycle.get()
                    else filtered_data["Ah-Cyc-Charge-0"]
                )
                y = filtered_data["U[V]"]
                plt.plot(x, y, label="Filtered Data (Charge-Voltage)", color="green")
                plt.xlabel("Charge (Ah)")
                plt.ylabel("Voltage (V)")
                plt.title("Filtered Data: Q vs U")

            else:
                messagebox.showerror("Error", "Invalid plot type selected.")
                return

            # Plot the fit if available
            if fit_data is not None:
                plt.plot(fit_data["x"], fit_data["y"], label="Fit (Linear Spline)", color="red", linestyle="--")

            # Highlight key values if the option is selected
            if self.visualize_key_values.get():
                key_points = self.extract_key_data(filtered_data)
                for point in key_points:
                    plt.scatter(point['x'], point['y'], color=point['color'], marker=point['marker'], s=100, label=point['label'])

            plt.legend()
            plt.grid(True)
            plt.show()

        except KeyError as e:
            messagebox.showerror("Error", f"Missing column in data: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def save_filtered_data(self):
        """
        Saves the filtered data to a user-specified directory with a preset filename in the 'filtered_data' folder.
        """
        # Synchronize dataset selection
        self.selected_filter_dataset.set(self.filter_dataset_selection.get())

        # Ensure a dataset is selected
        selected_type = self.selected_filter_dataset.get()
        if selected_type not in self.datasets or self.datasets[selected_type]["data"] is None:
            messagebox.showerror("Error", "No dataset selected or loaded. Please load data first.")
            return

        # Apply filtering to get the relevant dataset
        filtered_data, _ = self.apply_filters()
        if filtered_data is None or filtered_data.empty:
            messagebox.showerror("Error", "No data available after filtering.")
            return

        # Suggest a preset filename based on the original file and applied filters
        original_file = self.datasets[selected_type]["file_path"].get()
        if original_file == "No file selected":
            messagebox.showerror("Error", "No file selected to save filtered data.")
            return

        original_filename = os.path.basename(original_file)
        filename, ext = os.path.splitext(original_filename)

        filter_suffix = []
        if self.remove_pause.get():
            filter_suffix.append("nopause")
        if self.select_cycle.get():
            filter_suffix.append("cycle")
        if self.select_charge_half_cycle.get():
            filter_suffix.append("charge")
        if self.select_discharge_half_cycle.get():
            filter_suffix.append("discharge")
        preset_filename = f"{filename}-{'-'.join(filter_suffix)}.csv"

        # Default save directory
        save_folder = "filtered_data"
        os.makedirs(save_folder, exist_ok=True)  # Create folder if it doesn't exist
        default_save_path = os.path.join(save_folder, preset_filename)

        # Open a save dialog with the preset filename in the filtered_data directory
        save_path = filedialog.asksaveasfilename(
            title="Save Filtered Data",
            initialdir=save_folder,
            initialfile=preset_filename,
            filetypes=[("CSV Files", "*.csv"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if save_path:  # Save the file if the user provides a path
            try:
                filtered_data.to_csv(save_path, index=False)
                messagebox.showinfo("Success", f"Filtered data saved as {save_path}.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save filtered data: {e}")

    def extract_key_values(self):
        """
        Extracts key values from the filtered data based on user selection and displays them in a table.
        """
        # Synchronize dataset selection
        self.selected_filter_dataset.set(self.filter_dataset_selection.get())

        # Ensure a dataset is selected
        selected_type = self.selected_filter_dataset.get()
        if selected_type not in self.datasets or self.datasets[selected_type]["data"] is None:
            messagebox.showerror("Error", "No dataset selected or loaded. Please load data first.")
            return

        # Apply filtering to get the relevant dataset
        filtered_data, _ = self.apply_filters()

        if filtered_data is None or filtered_data.empty:
            messagebox.showerror("Error", "No data available after filtering.")
            return

        # Extract key values per cycle
        key_values = self.compute_key_values(filtered_data)

        if not key_values:
            messagebox.showinfo("No Key Values", "No key values were extracted based on the current selection.")
            return

        # Convert the key values into a DataFrame for display
        results_df = pd.DataFrame(key_values)

        # Show results in a new table
        self.show_results_table(results_df)


    def compute_key_values(self, filtered_data):
        """
        Computes key values per cycle.
        Returns a dictionary with cycle numbers as rows and selected key values as columns.
        """
        results = {"Cycle": []}  # Initialize results dictionary with "Cycle" as the first column

        # Add columns for each selected key value
        if self.extract_max_voltage.get():
            results["Max Voltage (V)"] = []
        if self.extract_max_charge.get():
            results["Max Charge (Ah)"] = []
        if self.extract_max_discharge.get():
            results["Max Discharge (Ah)"] = []

        # Group the data by cycle
        try:
            grouped_data = filtered_data.groupby("Cyc-Count")
            for cycle, group in grouped_data:
                results["Cycle"].append(cycle)

                # Calculate key values for this cycle
                if self.extract_max_voltage.get():
                    max_voltage = group["U[V]"].max()
                    results["Max Voltage (V)"].append(max_voltage)

                if self.extract_max_charge.get():
                    max_charge = group["Ah-Cyc-Charge-0"].max()
                    results["Max Charge (Ah)"].append(max_charge)

                if self.extract_max_discharge.get():
                    max_discharge = group["Ah-Cyc-Discharge-0"].max()
                    results["Max Discharge (Ah)"].append(max_discharge)

        except KeyError as e:
            messagebox.showerror("Error", f"Missing column in data: {e}")

        return results

    def show_results_table(self, data):
        """
        Displays the extracted values in a new window as a table.
        """
        results_window = tk.Toplevel(self.root)
        results_window.title("Extracted Key Values")
        results_window.geometry("600x400")

        # Add scrollbars
        x_scrollbar = tk.Scrollbar(results_window, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")

        y_scrollbar = tk.Scrollbar(results_window, orient="vertical")
        y_scrollbar.pack(side="right", fill="y")

        # Create a Text widget to display the data
        text = tk.Text(results_window, wrap="none", xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
        text.pack(side="left", fill="both", expand=True)

        # Configure the scrollbars to work with the Text widget
        x_scrollbar.config(command=text.xview)
        y_scrollbar.config(command=text.yview)

        # Insert the data into the Text widget
        text.insert("1.0", data.to_string(index=False))

        # Make the Text widget read-only
        text.config(state="disabled")

    def filter_data(self, data):
        """
        Applies selected filters to the given dataset and returns the filtered dataset.
        """
        # Synchronize dataset selection
        self.selected_filter_dataset.set(self.filter_dataset_selection.get())

        filtered_data = data.copy()

        if self.remove_pause.get():
            filtered_data = filtered_data[filtered_data['Command'] != 'Pause']

        if self.select_cycle.get():
            cycle_number = tk.simpledialog.askstring("Cycle Selection", "Enter Cycle Number:")
            if cycle_number is None:
                return None
            try:
                cycle_number = int(cycle_number)
                filtered_data = filtered_data[filtered_data['Cyc-Count'] == cycle_number]
            except ValueError:
                return None

        if self.select_charge_half_cycle.get():
            filtered_data = filtered_data[filtered_data['Command'].str.contains("Charge", na=False)]

        if self.select_discharge_half_cycle.get():
            filtered_data = filtered_data[filtered_data['Command'].str.contains("Discharge", na=False)]

        return filtered_data if not filtered_data.empty else None


    def compute_fit_data(self, filtered_data):
        """
        Computes fit data based on the selected plot and fit options.
        """
        fit_type = self.filter_fit_option.get()
        if fit_type == "linear spline":
            plot_type = self.filter_plot_option.get()
            if plot_type == "Q-U":
                x = (
                    filtered_data["Ah-Cyc-Discharge-0"]
                    if self.select_discharge_half_cycle.get()
                    else filtered_data["Ah-Cyc-Charge-0"]
                )
                y = filtered_data["U[V]"]
            elif plot_type == "U-t":
                x = filtered_data["Time[h]"]
                y = filtered_data["U[V]"]
            elif plot_type == "I-t":
                x = filtered_data["Time[h]"]
                y = filtered_data["I[A]"]
            else:
                return None

            return self.compute_linear_spline(x, y) if x is not None and y is not None else None

        return None

    def apply_filters(self):
        """
        Applies all selected filters to the current dataset.
        Computes fit data if a fit type is selected.
        Returns the filtered dataset and optional fit data.
        """
        # Synchronize dataset selection
        self.selected_filter_dataset.set(self.filter_dataset_selection.get())

        # Ensure a dataset is selected
        selected_type = self.selected_filter_dataset.get()
        if selected_type not in self.datasets or self.datasets[selected_type]["data"] is None:
            messagebox.showerror("Error", "No dataset selected or loaded. Please load data first.")
            return None, None

        # Get the currently selected dataset
        current_data = self.datasets[selected_type]["data"].copy()

        # Apply filters
        filtered_data = current_data

        if self.remove_pause.get():
            filtered_data = filtered_data[filtered_data['Command'] != 'Pause']

        if self.select_cycle.get():
            cycle_number = tk.simpledialog.askstring("Cycle Selection", "Enter Cycle Number:")
            if cycle_number is None:  # User pressed cancel or left it blank
                messagebox.showerror("Error", "No cycle number entered.")
                return None, None
            try:
                cycle_number = int(cycle_number)
                filtered_data = filtered_data[filtered_data['Cyc-Count'] == cycle_number]
            except ValueError:
                messagebox.showerror("Error", "Invalid cycle number entered.")
                return None, None

        if self.select_charge_half_cycle.get():
            filtered_data = filtered_data[filtered_data['Command'].str.contains("Charge", na=False)]

        if self.select_discharge_half_cycle.get():
            filtered_data = filtered_data[filtered_data['Command'].str.contains("Discharge", na=False)]

        if filtered_data.empty:
            messagebox.showerror("Error", "No data available after filtering.")
            return None, None

        # Handle fit data
        fit_data = None
        fit_type = self.filter_fit_option.get()
        if fit_type == "linear spline":
            plot_type = self.filter_plot_option.get()
            if plot_type == "Q-U":
                x = (
                    filtered_data["Ah-Cyc-Discharge-0"]
                    if self.select_discharge_half_cycle.get()
                    else filtered_data["Ah-Cyc-Charge-0"]
                )
                y = filtered_data["U[V]"]
            elif plot_type == "U-t":
                x = filtered_data["Time[h]"]
                y = filtered_data["U[V]"]
            elif plot_type == "I-t":
                x = filtered_data["Time[h]"]
                y = filtered_data["I[A]"]
            else:
                x, y = None, None

            if x is not None and y is not None:
                fit_data = self.compute_linear_spline(x, y)

        return filtered_data, fit_data

    def compute_linear_spline(self, x, y):
        """
        Computes linear spline fit for given x and y data.
        Returns a dictionary with x and y values for the spline.
        """
        from scipy.interpolate import interp1d

        spline = interp1d(x, y, kind="linear", fill_value="extrapolate")
        x_fit = np.linspace(x.min(), x.max(), 500)
        y_fit = spline(x_fit)

        return {"x": x_fit, "y": y_fit}

    def extract_key_data(self, filtered_data):
        """
        Extracts key values relevant to the current plot type and user selections.
        Returns a list of dictionaries with the following structure:
        [{'x': ..., 'y': ..., 'color': ..., 'marker': ..., 'label': ...}]
        """
        key_points = []
        plot_type = self.filter_plot_option.get()

        # Extract key data based on plot type
        if plot_type == "U-t" and self.extract_max_voltage.get():
            max_voltage = filtered_data['U[V]'].max()
            time_at_max_voltage = filtered_data.loc[filtered_data['U[V]'] == max_voltage, 'Time[h]'].iloc[0]
            key_points.append({
                'x': time_at_max_voltage,
                'y': max_voltage,
                'color': 'blue',
                'marker': 'o',
                'label': "Max Voltage"
            })

        if plot_type == "I-t" and self.extract_max_charge.get():
            max_current = filtered_data['I[A]'].max()
            time_at_max_current = filtered_data.loc[filtered_data['I[A]'] == max_current, 'Time[h]'].iloc[0]
            key_points.append({
                'x': time_at_max_current,
                'y': max_current,
                'color': 'orange',
                'marker': 'x',
                'label': "Max Current"
            })

        if plot_type == "Q-U":
            if self.extract_max_charge.get():
                max_charge = filtered_data['Ah-Cyc-Charge-0'].max()
                voltage_at_max_charge = filtered_data.loc[filtered_data['Ah-Cyc-Charge-0'] == max_charge, 'U[V]'].iloc[0]
                key_points.append({
                    'x': max_charge,
                    'y': voltage_at_max_charge,
                    'color': 'green',
                    'marker': 'o',
                    'label': "Q max (Charge)"
                })

            if self.extract_max_discharge.get():
                max_discharge = filtered_data['Ah-Cyc-Discharge-0'].max()
                voltage_at_max_discharge = filtered_data.loc[filtered_data['Ah-Cyc-Discharge-0'] == max_discharge, 'U[V]'].iloc[0]
                key_points.append({
                    'x': max_discharge,
                    'y': voltage_at_max_discharge,
                    'color': 'red',
                    'marker': '^',
                    'label': "Q max (Discharge)"
                })

        return key_points

    def split_data_by_cycle(self):
        """
        Splits the current dataset by cycle number and stores the grouped data.
        """
        dataset_type = self.current_dataset_type.get().split()[0].lower()
        data = self.datasets.get(dataset_type, {}).get("data")
        if data is None:
            messagebox.showerror("Error", "No dataset loaded.")
            return

        if "Cyc-Count" not in data.columns:
            messagebox.showerror("Error", "The dataset does not contain a 'Cyc-Count' column.")
            return

        # Group the data by cycle
        self.cycle_data = data.groupby("Cyc-Count")
        messagebox.showinfo("Success", "Data has been split by cycle.")

if __name__ == "__main__":
    root = tk.Tk()
    app = HC2FCApp(root)
    root.mainloop()
