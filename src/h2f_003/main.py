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
from data_handling import ModifyDataWidget, FilterWidget, KeyValuesWidget
from plotting import MultiGraphPlotter
from ui_widgets import DataWidget, FilteredDataBrowser
from styles import UIStyling

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
        '''
            # Dropdown for selecting plot type
            tk.Label(multi_graph_frame, text="Select Plot Type:").pack(side="left", padx=5)
            self.multi_graph_plot_option = tk.StringVar(value="U-t (Voltage-Time)")
            plot_options = ["U-t (Voltage-Time)", "I-t (Current-Time)", "Q-U (Charge-Voltage)"]
            tk.OptionMenu(multi_graph_frame, self.multi_graph_plot_option, *plot_options).pack(side="left", padx=5)
        ''' 
        # Dropdown for selecting plot type
        tk.Label(multi_graph_frame, text="Select Plot Type:", font=UIStyling.LABEL_FONT).pack(side="left", padx=UIStyling.DROPDOWN_PADX)

        self.multi_graph_plot_option = tk.StringVar(value="U-t (Voltage-Time)")
        plot_options = ["U-t (Voltage-Time)", "I-t (Current-Time)", "Q-U (Charge-Voltage)"]

        self.multi_graph_dropdown = tk.OptionMenu(multi_graph_frame, self.multi_graph_plot_option, *plot_options)
        self.multi_graph_dropdown.config(font=UIStyling.DROPDOWN_FONT)  # Apply styling
        self.multi_graph_dropdown.pack(side="left", padx=UIStyling.DROPDOWN_PADX)

        # Plot Multi-Graph Button
        tk.Button(multi_graph_frame, text="Plot Multi-Graph", command=self._plot_multi_graph).pack(side="left", padx=10)

    def save_project_callback(self):
        """
        Opens a file dialog for the user to save a project file and then calls save_project().
        """
        # Set the default folder to 'projects'
        save_folder = os.path.join(os.getcwd(), "projects")
        os.makedirs(save_folder, exist_ok=True)  # Ensure the folder exists

        file_path = filedialog.asksaveasfilename(
            defaultextension=".hc2fcproj",
            filetypes=[("HC2FC Project Files", "*.hc2fcproj"), ("All Files", "*.*")],
            title="Save Project",
            initialdir=save_folder  # ✅ Default directory is now "projects"
        )
        
        if file_path:  # Ensure user didn't cancel the dialog
            self.save_project(file_path)  # Call save_project with the selected file path

    def save_project(self, project_path):
        """
        Saves the project as a .hc2fcproj ZIP file containing JSON metadata and stored datasets.
        """
        try:
            project_data = {
                "original_files": {
                    "anode": self.datasets["anode"]["file_path"].get(),
                    "cathode": self.datasets["cathode"]["file_path"].get()
                },
                "datasets": {},  # Store dataset metadata
                "filters": {},   # Store current filter settings (Updated)
                "plots": [],     # Store plot metadata (optional for now)
            }

            # ✅ Save filtered datasets (only storing dataset names)
            for dataset_type, datasets in self.filtered_datasets.items():
                project_data["datasets"][dataset_type] = [dataset["name"] for dataset in datasets]

            # ✅ Fetch the latest filter settings from the UI at the moment of saving
            for dataset_type in ["anode", "cathode"]:
                widget = self.anode_filter_widget if dataset_type == "anode" else self.cathode_filter_widget
                project_data["filters"][dataset_type] = {
                    "remove_pause": widget.remove_pause.get(),
                    "select_cycle": widget.select_cycle.get(),
                    "selected_cycle": widget.cycle_selection.get(),
                    "stepchange": widget.apply_step_change.get(),
                    "select_charge_half_cycle": widget.select_charge_half_cycle.get(),
                    "select_discharge_half_cycle": widget.select_discharge_half_cycle.get(),
                    "plot_type": widget.plot_option.get()
                }

            # ✅ Save project data to ZIP file
            with zipfile.ZipFile(project_path, "w", zipfile.ZIP_DEFLATED) as project_zip:
                metadata_json = json.dumps(project_data, indent=4)
                project_zip.writestr("project_metadata.json", metadata_json)

                # ✅ Save original anode and cathode datasets
                for dataset_type in ["anode", "cathode"]:
                    original_file_name = self.datasets[dataset_type]["file_path"].get()
                    dataset_df = self.datasets[dataset_type]["data"]
                    
                    if dataset_df is not None and original_file_name != "No file selected":
                        dataset_csv = dataset_df.to_csv(index=False)
                        project_zip.writestr(f"datasets/{original_file_name}.csv", dataset_csv)  # ✅ Save original dataset

                # ✅ Save filtered datasets
                for dataset_type, datasets in self.filtered_datasets.items():
                    for dataset in datasets:
                        dataset_csv = dataset["data"].to_csv(index=False)
                        project_zip.writestr(f"datasets/{dataset['name']}.csv", dataset_csv)

            print(f"✅ Project saved successfully at: {project_path}")

        except Exception as e:
            print(f"❌ Error saving project: {e}")

    def load_project_callback(self):
        """
        Opens a file dialog for the user to select a project file and then calls load_project().
        """
        file_path = filedialog.askopenfilename(
            filetypes=[("HC2FC Project Files", "*.hc2fcproj"), ("All Files", "*.*")],
            title="Load Project"
        )
        
        if file_path:  # Ensure user didn't cancel the dialog
            self.load_project(file_path)  # Call load_project with the selected file path

    def load_project(self, project_path):
        """
        Loads a .hc2fcproj file, restoring datasets, filters, and plots.
        Clears any manually loaded data before loading the project.
        """
        try:
            with zipfile.ZipFile(project_path, "r") as project_zip:
                if "project_metadata.json" not in project_zip.namelist():
                    print("❌ Error: project_metadata.json is missing from the project file.")
                    return
                
                metadata_json = project_zip.read("project_metadata.json").decode()
                project_data = json.loads(metadata_json)

                # ✅ Step 1: Clear all currently loaded data before loading the project
                self.datasets = {
                    "anode": {"data": None, "file_path": tk.StringVar(value="No file selected")},
                    "cathode": {"data": None, "file_path": tk.StringVar(value="No file selected")},
                }
                self.filtered_datasets = {"anode": [], "cathode": [], "full_cell": []}
                self.modified_datasets = {"anode": None, "cathode": None}

                # ✅ Clear UI elements
                self.anode_browser.clear_browser()
                self.cathode_browser.clear_browser()
                self.full_cell_browser.clear_browser()

                # ✅ Step 2: Restore main anode & cathode datasets
                original_files = project_data.get("original_files", {})
                for dataset_type in ["anode", "cathode"]:
                    original_filename = original_files.get(dataset_type, "")
                    
                    # ✅ Ensure the original dataset exists in the project ZIP
                    if original_filename and f"datasets/{original_filename}.csv" in project_zip.namelist():
                        with project_zip.open(f"datasets/{original_filename}.csv") as dataset_file:
                            dataset_df = pd.read_csv(dataset_file)

                            # ✅ Restore to main dataset
                            print(f"✅ Restoring original {dataset_type} dataset: {original_filename}")
                            self.datasets[dataset_type]["data"] = dataset_df
                            self.datasets[dataset_type]["file_path"].set(original_filename)  # Update UI

                    else:
                        print(f"⚠️ Warning: Original {dataset_type} dataset '{original_filename}' not found in project.")

                # ✅ Restore filtered datasets
                for dataset_type, dataset_list in project_data["datasets"].items():
                    for dataset_name in dataset_list:
                        dataset_csv_path = f"datasets/{dataset_name}.csv"
                        if dataset_csv_path in project_zip.namelist():
                            with project_zip.open(dataset_csv_path) as dataset_file:
                                dataset_df = pd.read_csv(dataset_file)
                                
                                self.filtered_datasets[dataset_type].append(
                                    {"name": dataset_name, "data": dataset_df}
                                )

                # ✅ Restore UI for datasets
                for dataset in self.filtered_datasets["anode"]:
                    self.anode_browser.add_dataset(dataset["name"])
                for dataset in self.filtered_datasets["cathode"]:
                    self.cathode_browser.add_dataset(dataset["name"])
                for dataset in self.filtered_datasets["full_cell"]:
                    self.full_cell_browser.add_dataset(dataset["name"])

                # ✅ Step 3: Update UI file paths for anode/cathode main datasets
                if self.datasets["anode"]["data"] is not None:
                    self.anode_widget.file_label.config(text=self.datasets["anode"]["file_path"].get())

                if self.datasets["cathode"]["data"] is not None:
                    self.cathode_widget.file_label.config(text=self.datasets["cathode"]["file_path"].get())

                print("✅ Datasets successfully restored in UI.")

                # ✅ Step 4: Restore filter settings
                for dataset_type in ["anode", "cathode"]:
                    widget = self.anode_filter_widget if dataset_type == "anode" else self.cathode_filter_widget
                    if dataset_type in project_data["filters"]:
                        filter_data = project_data["filters"][dataset_type]
                        widget.remove_pause.set(filter_data.get("remove_pause", False))
                        widget.select_cycle.set(filter_data.get("select_cycle", False))
                        widget.cycle_selection.set(filter_data.get("selected_cycle", "All"))
                        widget.apply_step_change.set(filter_data.get("stepchange", False))
                        widget.select_charge_half_cycle.set(filter_data.get("select_charge_half_cycle", False))
                        widget.select_discharge_half_cycle.set(filter_data.get("select_discharge_half_cycle", False))
                        widget.plot_option.set(filter_data.get("plot_type", "U-t (Voltage-Time)"))

                print("✅ Filters successfully restored.")

                # ✅ Step 5: Restore plots
                self.loaded_plots = []  # Clear any existing plots
                for file_name in project_zip.namelist():
                    if file_name.startswith("plot_") and file_name.endswith(".png"):
                        with project_zip.open(file_name) as plot_file:
                            img_data = plot_file.read()
                            image = Image.open(io.BytesIO(img_data))
                            self.loaded_plots.append(image)

                if self.loaded_plots:
                    print(f"✅ Restored {len(self.loaded_plots)} plots from the project file.")

            print("🎉 Project loaded successfully!")

        except Exception as e:
            print(f"❌ Error loading project: {e}")

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

                # Update cycle dropdown options if 'Cyc-Count' column exists
                if "Cyc-Count" in data.columns:
                    unique_cycles = sorted(data["Cyc-Count"].unique())
                    if dataset_type == "anode":
                        self.anode_filter_widget.update_cycle_options(unique_cycles)
                    else:
                        self.cathode_filter_widget.update_cycle_options(unique_cycles)

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

if __name__ == "__main__":
    root = tk.Tk()
    app = HC2FCApp(root)
    root.mainloop()
