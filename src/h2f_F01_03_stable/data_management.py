import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d


class DataManager:
    """
    Handles dataset selection, loading, visualization, and plotting.
    """

    def __init__(self, app_context):
        self.app = app_context  # Reference to HC2FCApp instance

        # Datasets dictionary
        self.datasets = {
            "anode": {"data": None, "file_path": tk.StringVar(value="No file selected")},
            "cathode": {"data": None, "file_path": tk.StringVar(value="No file selected")},
            "full_cell": {"data": None, "file_path": tk.StringVar(value="No file selected")},            
        }
        self.filtered_datasets = {"anode": [], "cathode": [], "full_cell": []}
        self.modified_datasets = {"anode": None, "cathode": None, "full_cell": None}

### data import and quick check methods

    def load_dataset(self, dataset_type, file_path):
        """
        Loads a dataset from a file and updates the application state.
        """
        try:
            # Load dataset
            data = pd.read_csv(file_path, skiprows=12, delimiter=",", encoding="utf-8", on_bad_lines="skip")
            self.datasets[dataset_type]["data"] = data
            self.datasets[dataset_type]["file_path"].set(os.path.basename(file_path))  # Update UI label


            '''
                # ✅ Update cycle dropdown options dynamically
                if "Cyc-Count" in data.columns:
                    unique_cycles = sorted(data["Cyc-Count"].unique())

                    # ✅ Dynamically update the correct filter widget
                    if dataset_type in self.app.filter_widgets:
                        self.app.filter_widgets[dataset_type].update_cycle_options(unique_cycles)
                
            '''
            # ✅ Check which cycle column is available
            cycle_column = "Cyc-Count" if "Cyc-Count" in data.columns else "abs_cycle" if "abs_cycle" in data.columns else None
            
            if cycle_column:
                unique_cycles = sorted(data[cycle_column].unique())

                # ✅ Dynamically update the correct filter widget
                if dataset_type in self.app.filter_widgets:
                    self.app.filter_widgets[dataset_type].update_cycle_options(unique_cycles)
     
            # ✅ Update ModifyDataWidget dropdown
            self.update_modify_widgets(dataset_type)
                
            messagebox.showinfo("Success", f"{dataset_type.capitalize()} dataset loaded.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load {dataset_type} dataset: {e}")

    def select_file(self, dataset_type):
        """
        Allows the user to select a dataset file and loads it.
        """
        initial_dir = os.path.join(os.getcwd(), "data")  # Default to /data subfolder
        file_path = filedialog.askopenfilename(
            title=f"Select {dataset_type.capitalize()} Data File",
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*.*")],
            initialdir=initial_dir,
        )
        if file_path:
            self.load_dataset(dataset_type, file_path)

    def show_data_table(self, dataset_type):
        """
        Displays the selected dataset in a table.
        """
        data = self.datasets.get(dataset_type, {}).get("data")
        if data is None:
            messagebox.showerror("Error", f"No {dataset_type} dataset loaded.")
            return

        # Create a new window for displaying data
        table_window = tk.Toplevel(self.app.root)
        table_window.title(f"Data Table - {dataset_type.capitalize()}")
        table_window.geometry("800x600")

        # Add scrollbars
        x_scrollbar = tk.Scrollbar(table_window, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")
        y_scrollbar = tk.Scrollbar(table_window, orient="vertical")
        y_scrollbar.pack(side="right", fill="y")

        # Text widget for displaying the data
        text = tk.Text(table_window, wrap="none", xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
        text.pack(side="left", fill="both", expand=True)

        x_scrollbar.config(command=text.xview)
        y_scrollbar.config(command=text.yview)

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

    def get_dataset(self, dataset_type):
        """ Returns the dataset for the given type ('anode' or 'cathode'). """
        return self.datasets.get(dataset_type, {}).get("data", None)

### update ModifyDataWidget dropdowns

    def update_modify_widgets(self, dataset_type):
            """
            Updates the ModifyDataWidget dropdown with available column names from the dataset.
            """
            dataset = self.datasets.get(dataset_type, {}).get("data")


            # ✅ Check if the dataset type exists in modify_widgets before updating
            widget = self.app.modify_widgets.get(dataset_type)
            
        #    widget = self.app.modify_widgets["anode"] if dataset_type == "anode" else self.app.modify_widgets["cathode"]

            if dataset is not None:
                column_names = dataset.columns.tolist()
                widget.update_column_dropdown(column_names)
            else:
                widget.update_column_dropdown([])  # Clear dropdown if no dataset is loaded

### filter methods

    def apply_filters(self, dataset_type):
        """
        Applies selected filters and modifications to the given dataset.
        """
        filter_options = self.app.get_filter_options(dataset_type) ## this is how i should have done it in the beginning
        print(filter_options)
        data = self.datasets.get(dataset_type, {}).get("data")
        if data is None:
            messagebox.showerror("Error", f"No {dataset_type} dataset loaded.")
            return None

        filtered_data = data.copy()
        
        if dataset_type not in self.app.filter_widgets:
            messagebox.showerror("Error", f"No filter widget found for {dataset_type}.")
            return None  # Exit early if the widget is missing

        widget = self.app.filter_widgets[dataset_type]
        modify_widget = self.app.modify_widgets.get(dataset_type) #hkw

        ### Filters
        # Pause filter
        if widget.remove_pause.get():
            filtered_data = filtered_data[filtered_data['Command'] != 'Pause']

        # Cycle filter
        cycle_column = widget.cycle_column.get()  # "Cyc-Count" or "abs_cycle"

        if widget.select_cycle.get():
            selected_cycle = widget.cycle_selection.get()
            cycle_column = widget.cycle_column.get()  # Get selected cycle column

            # Ensure `abs_cycle` is computed before filtering
            if cycle_column == "abs_cycle" and "abs_cycle" not in filtered_data.columns:
                filtered_data = self.compute_absolute_cycle(filtered_data)  # Compute abs_cycle
            
            # Now check if column exists after computing it
            if selected_cycle and selected_cycle != "All":
                if cycle_column in filtered_data.columns:
                    filtered_data = filtered_data[filtered_data[cycle_column] == int(selected_cycle)]
                else:
                    messagebox.showerror("Error", f"Column '{cycle_column}' not found in dataset.")
                    return None  # ✅ Exit early if column is missing        
        # Charge and discharge half cycle filter
        if widget.select_charge_half_cycle.get():
            filtered_data = filtered_data[filtered_data['Command'].str.contains("Charge", na=False)]
        if widget.select_discharge_half_cycle.get():
            filtered_data = filtered_data[filtered_data['Command'].str.contains("Discharge", na=False)]

        # Step Change Filter
        if widget.apply_step_change.get():
            step_column = widget.step_change_column.get()
            if step_column in filtered_data.columns:
                filtered_data = self.step_change_filter(filtered_data, step_column)
            else:
                messagebox.showerror("Error", f"Column '{step_column}' not found in dataset.")

        # Range Filter
        if widget.apply_range_filter.get():
            selected_column = widget.selected_column.get()
            min_value, max_value = widget.min_value.get(), widget.max_value.get()

            if selected_column in filtered_data.columns:
                filtered_data = filtered_data[(filtered_data[selected_column] >= min_value) & (filtered_data[selected_column] <= max_value)]
            else:
                messagebox.showerror("Error", f"Column '{selected_column}' not found in dataset.")

        ### Data modifications
        # Absolute cycle modification
        if modify_widget.compute_abs_cycle.get():
            filtered_data = self.compute_absolute_cycle(filtered_data)

        # dQ/dU modification
        if modify_widget.compute_du_dq.get():
            if "Ah-Cyc-Charge-0" in filtered_data.columns and "U[V]" in filtered_data.columns:
                filtered_data["dU/dQ"] = np.gradient(filtered_data["U[V]"], filtered_data["Ah-Cyc-Charge-0"])

        # Normalize voltage modification
        if modify_widget.normalize_voltage.get():
            if "U[V]" in filtered_data.columns:
                max_voltage = filtered_data["U[V]"].max()
                filtered_data["U_normalized"] = filtered_data["U[V]"] / max_voltage

        # Apply Offset Modification
        if modify_widget.apply_offset.get():
            offset_column = modify_widget.selected_column.get()
            offset_value = modify_widget.offset_value.get()
            if offset_column and offset_column in filtered_data.columns:
                filtered_data[offset_column] += offset_value  # ✅ Modify the column directly

        # ✅ If "Fit Data" is selected, generate fit data instead of returning filtered data
#        print("I-t Debug: Checking available columns:", filtered_data.columns) # DEBUG
#        print("I-t Debug: Missing values in I[A]:", filtered_data["I[A]"].isna().sum()) # DEBUG
#        print("I-t Debug: Unique I[A] values:", filtered_data["I[A]"].nunique()) # DEBUG


        # Generate fit data for Store/Save filtered data
        if widget.data_type_selection.get() == "Fit Data":
            if widget.fit_option.get() != "linear spline":
                messagebox.showerror("Error", "Linear spline fit must be selected to generate Fit Data.")
                return None

            # ✅ Determine columns dynamically based on the selected plot type
            plot_type = widget.plot_option.get()
        #    print(f"Using plot type: {plot_type}") # DEBUGGING CODE, REMOVE ME!
            
            '''
            column_map = {
                            "U-t": ("Time[h]", "U[V]"),
                            "I-t": ("Time[h]", "I[A]"),
                            "Q-U": ("Ah-Cyc-Charge-0", "U[V]"),
                        }

                        if plot_type not in column_map:
                            messagebox.showerror("Error", f"Invalid plot type '{plot_type}' selected.")
                            return None

                        x_col, y_col = column_map[plot_type]            
            '''

            # Adjust x_col based on charge/discharge selection
            if plot_type == "Q-U":
                if widget.select_charge_half_cycle.get():
                    x_col = "Ah-Cyc-Charge-0"
                elif widget.select_discharge_half_cycle.get():
                    x_col = "Ah-Cyc-Discharge-0"
                else:
                    messagebox.showerror("Error", "Please select either Charge or Discharge filter when using Q-U.")
                    return None  # Prevent further execution
                
                y_col = "U[V]"

            else:
                column_map = {
                    "U-t": ("Time[h]", "U[V]"),
                    "I-t": ("Time[h]", "I[A]"),
                }
                if plot_type not in column_map:
                    messagebox.showerror("Error", f"Invalid plot type '{plot_type}' selected.")
                    return None
                x_col, y_col = column_map[plot_type]
            
            # Ensure required columns exist
            if not all(col in filtered_data.columns for col in [x_col, y_col]):
                messagebox.showerror("Error", f"Dataset must contain columns: {x_col}, {y_col}")
                return None
            
            # Ensure x_col is strictly increasing
            if not all(np.diff(filtered_data[x_col]) > 0):
                messagebox.showerror(
                    "Error",
                    "X-values must be strictly increasing. Adjust filter settings to prevent duplicate or decreasing values!"
                )
                return None
    

            try:
                # ✅ If "Use Step Size" is active, pass step size to compute_linear_spline
                if widget.use_step_size.get() and widget.step_size_value.get() > 0:
                    step_size = widget.step_size_value.get()
                    fit_data = self.compute_linear_spline(filtered_data[x_col], filtered_data[y_col], step_size)
                else:
                    fit_data = self.compute_linear_spline(filtered_data[x_col], filtered_data[y_col])

                if fit_data is None:
                    return None
    
                # Convert to DataFrame with row numbers
                fit_df = pd.DataFrame({x_col: fit_data["x"], y_col: fit_data["y"]})
                fit_df["row"] = range(len(fit_df))

                return fit_df
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate fit data: {e}")
                return None


        return filtered_data  # ✅ Always return the modified dataset

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
    
    def _generate_filter_suffix(self, dataset_type):
        """
        Generate a suffix string based on the applied filters.
        """
        if dataset_type not in self.app.filter_widgets:
            messagebox.showerror("Error", f"No filter widget found for {dataset_type}.")
            return None  # Exit early if the widget is missing
        widget = self.app.filter_widgets[dataset_type]
        suffixes = []

        if widget.remove_pause.get():
            suffixes.append("nopause")
        if widget.select_cycle.get():
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

        if widget.apply_range_filter.get():
            selected_column = widget.selected_column.get()
            min_value, max_value = widget.min_value.get(), widget.max_value.get()
            suffixes.append(f"{selected_column}_range_{min_value}-{max_value}")

        # ✅ Range Filter integration
        if widget.apply_range_filter.get():
            selected_column = widget.selected_column.get()
            if selected_column and selected_column != "Select Column":
                min_value, max_value = widget.min_value.get(), widget.max_value.get()
                suffixes.append(f"{selected_column}_range_{min_value}-{max_value}")

        return "-".join(suffixes) if suffixes else "nofilter"

### modification methods

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

        # Apply Offset if enabled
        if widget.apply_offset.get():
            offset_column = widget.selected_column.get()
            offset_value = widget.offset_value.get()
            if offset_column and offset_column in modified_data.columns:
                modified_data[f"{offset_column}_offset"] = modified_data[offset_column] + offset_value

        # Store the latest modified dataset instead of appending to a list
        self.modified_datasets[dataset_type] = modified_data

        messagebox.showinfo("Success", f"Modified dataset stored for {dataset_type}.")

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

    def _generate_modification_suffix(self, dataset_type):
        """
        Generate a suffix string based on the applied modifications.
        """
    #    modify_widget = self.app.modify_widgets["anode"] if dataset_type == "anode" else self.app.modify_widgets["cathode"]
        modify_widget = self.app.modify_widgets.get(dataset_type)
        suffixes = []

        if modify_widget.compute_abs_cycle.get():
            suffixes.append("abs_cycle")
        if modify_widget.compute_du_dq.get():
            suffixes.append("du_dq")
        if modify_widget.normalize_voltage.get():
            suffixes.append("U_norm")
        if modify_widget.apply_offset.get():
            suffixes.append(f"offset_{modify_widget.selected_column.get()}")

        return "-".join(suffixes) if suffixes else "nomod"

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

### value extraction methods

    def compute_key_values(self, dataset_type):
        """
        Computes key values (max voltage, max charge, max discharge) for the filtered dataset.
        Returns a dictionary of results.
        """
        filtered_data = self.apply_filters(dataset_type)
        if filtered_data is None:
            return None

        if dataset_type not in self.app.key_values_widgets:
            messagebox.showerror("Error", f"No key_values widget found for {dataset_type}.")
            return None  # Exit early if the widget is missing

        widget = self.app.key_values_widgets[dataset_type]

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

    def extract_key_values(self, dataset_type):
        """
        Extracts and displays key values for the selected dataset type.
        """
        results = self.compute_key_values(dataset_type)
        self.show_key_values_table(results, dataset_type)

    def show_key_values_table(self, results, dataset_type):
        """
        Displays the computed key values in a new window.
        """
        if results is None:
            messagebox.showerror("Error", f"Failed to compute key values for {dataset_type}.")
            return

        # Create a new window for the results
        results_window = tk.Toplevel(self.app.root)
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
        results_df = pd.DataFrame(results)
        text.insert("1.0", results_df.to_string(index=False))

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

### fit methods

    def compute_linear_spline(self, x, y, step_size=None, num_points=500):
        """
        Computes a linear spline fit for given x and y data.
        
        Parameters:
        - x (array-like): The independent variable (e.g., charge in Ah).
        - y (array-like): The dependent variable (e.g., voltage in V).
        - step_size (float, optional): The desired spacing between generated x values.
        - num_points (int, optional): Number of evenly spaced points if step_size is not given.

        Returns:
        - dict: A dictionary with interpolated 'x' and 'y' values.
        """
        try:
            spline = interp1d(x, y, kind="linear", fill_value="extrapolate")

            if step_size:
                # Generate x values based on step size
                x_fit = np.arange(x.min(), x.max(), step_size)
            else:
                # Default behavior: Generate evenly spaced points
                x_fit = np.linspace(x.min(), x.max(), num_points)
            
            y_fit = spline(x_fit)

            return {"x": x_fit, "y": y_fit}

        except Exception as e:
            messagebox.showerror("Error", f"Failed to compute linear spline: {e}")
            return None




### save as .csv and store in data browser - modified and filtered data

### suffix creation for data selection filtered/fit data

    # hkw updated method needs to be checked if working, after fix to apply_filters!
    def _generate_datatype_suffix(self, dataset_type):
        """
        Generate a suffix string based on the selected data type (Modified vs Fit).
        If "Fit Data" is selected and step size is applied, add "_step_<value>_" after "_FitData_linSpline".
        """
        filter_widget = self.app.filter_widgets.get(dataset_type)
        if not filter_widget:
            return ""  # Default: No suffix if no filter widget found

        suffix = ""

        # Check if fit data is selected
        if filter_widget.data_type_selection.get() == "Fit Data":
            suffix += "_FitData_linSpline"

            # Check if "Use Step Size" is active
            if filter_widget.use_step_size.get() and filter_widget.step_size_value.get() > 0:
                step_value = filter_widget.step_size_value.get()
                suffix += f"_step_{step_value}"

            '''
            # Check if step size is applied
            if hasattr(filter_widget, "step_size") and filter_widget.step_size.get() > 0:
                step_value = filter_widget.step_size.get()
                suffix += f"_step_{step_value}"            
            '''    
        return suffix  # Default: No suffix for modified data

    def save_filtered_data(self, dataset_type):
        """
        Saves the filtered data to a user-specified file, with suffixes describing applied filters and modifications.
        """
        
        filter_options = self.app.get_filter_options(dataset_type) ## this is how i should have done it in the beginning

        filtered_data = self.apply_filters(dataset_type)
        if filtered_data is None:
            return
        
        # get original filename
        dataset_file = self.datasets[dataset_type]["file_path"].get()
        if dataset_file == "No file selected":
            messagebox.showerror("Error", f"No {dataset_type} file loaded.")
            return

        base_filename = os.path.splitext(os.path.basename(dataset_file))[0]
        filter_suffix = self._generate_filter_suffix(dataset_type)
        modification_suffix = self._generate_modification_suffix(dataset_type)
        datatype_suffix = self._generate_datatype_suffix(dataset_type)
        suggested_filename = f"{base_filename}_{filter_suffix}_{modification_suffix}_{datatype_suffix}.csv"

        save_folder = os.path.join(os.getcwd(), "filtered_data")
        os.makedirs(save_folder, exist_ok=True)

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

    def store_filtered_data(self, dataset_type):
        """
        Store the filtered dataset in the respective browser.
        """
 #       filter_options = self.app.get_filter_options(dataset_type) ## this is how i should have done it in the beginning
 #       data_to_save = fit_data if filter_options["data_type_selection"] == "Fit Data" else filtered_data
        


        if self.datasets[dataset_type]["data"] is None:
            messagebox.showerror("Error", f"No {dataset_type} data loaded.")
            return

        filtered_data = self.apply_filters(dataset_type)
        if filtered_data is None or filtered_data.empty:
            messagebox.showerror("Error", f"No data available after filtering {dataset_type}.")
            return

        dataset_file = self.datasets[dataset_type]["file_path"].get()
        if dataset_file == "No file selected":
            dataset_file = "Unknown"

        filter_suffix = self._generate_filter_suffix(dataset_type)
        modification_suffix = self._generate_modification_suffix(dataset_type)
        datatype_suffix = self._generate_datatype_suffix(dataset_type)
        dataset_name = f"{os.path.splitext(dataset_file)[0]}_{filter_suffix}_{modification_suffix}_{datatype_suffix}"

        self.filtered_datasets[dataset_type].append({"name": dataset_name, "data": filtered_data})

        if dataset_type not in self.app.data_browsers:
            messagebox.showerror("Error", f"No data browser found for {dataset_type}.")
            return

        data_browser = self.app.data_browsers[dataset_type]
        data_browser.add_dataset(dataset_name)

        messagebox.showinfo("Success", f"Filtered dataset stored: {dataset_name}")

### plot modified and filtered data

    def plot_filtered_data(self, dataset_type):
        """
        Plots the filtered data for the selected dataset type, supporting:
        - 'Show Cycles' with an option to use 'Cyc-Count' or 'abs_cycle'
        - 'Linear Spline'
        - 'Show Key Values'
        """
        filtered_data = self.apply_filters(dataset_type)  # ✅ Use DataManager
        if filtered_data is None:
            return

        # Get the filter and key value widgets for the dataset
        if dataset_type not in self.app.filter_widgets:
            messagebox.showerror("Error", f"No filter widget found for {dataset_type}.")
            return None  # Exit early if the widget is missing

        filter_widget = self.app.filter_widgets[dataset_type]


        if dataset_type not in self.app.key_values_widgets:
            messagebox.showerror("Error", f"No key_values widget found for {dataset_type}.")
            return None  # Exit early if the widget is missing

        key_values_widget = self.app.key_values_widgets[dataset_type]


        plot_type = filter_widget.plot_option.get()
        show_cycles = filter_widget.show_cycles.get()
        fit_type = filter_widget.fit_option.get()
        show_key_values = filter_widget.visualize_key_values.get()
        use_step_size = filter_widget.use_step_size.get()  # New: Check if step size is enabled
        step_size = filter_widget.step_size_value.get() if use_step_size else None  # New: Get step size value if enabled


        # Get the cycle column selection from the dropdown (default: Cyc-Count)
        cycle_column = filter_widget.cycle_column.get()  # "Cyc-Count" or "abs_cycle"   -hkw

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

            # Linear Spline functionality with step size
            if fit_type == "linear spline":
                spline_data = self.compute_linear_spline(x, y, step_size=step_size)  # Pass step_size if available
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
