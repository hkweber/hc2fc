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
        }
        self.filtered_datasets = {"anode": [], "cathode": [], "full_cell": []}
        self.modified_datasets = {"anode": None, "cathode": None}

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

            # Update cycle dropdown options if 'Cyc-Count' column exists
            if "Cyc-Count" in data.columns:
                unique_cycles = sorted(data["Cyc-Count"].unique())
                if dataset_type == "anode":
                    self.app.anode_filter_widget.update_cycle_options(unique_cycles)
                else:
                    self.app.cathode_filter_widget.update_cycle_options(unique_cycles)

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

### other methods

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

### filter methods

    def apply_filters(self, dataset_type):
        """
        Applies selected filters and modifications to the given dataset.
        """
        data = self.datasets.get(dataset_type, {}).get("data")
        if data is None:
            messagebox.showerror("Error", f"No {dataset_type} dataset loaded.")
            return None

        filtered_data = data.copy()

        widget = self.app.anode_filter_widget if dataset_type == "anode" else self.app.cathode_filter_widget
        modify_widget = self.app.anode_modify_widget if dataset_type == "anode" else self.app.cathode_modify_widget

        # ✅ Apply standard filters
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

        # ✅ Step Change Filtering
        if widget.apply_step_change.get():
            step_column = widget.step_change_column.get()
            if step_column in filtered_data.columns:
                filtered_data = self.step_change_filter(filtered_data, step_column)
            else:
                messagebox.showerror("Error", f"Column '{step_column}' not found in dataset.")

        # ✅ Apply Range Filter
        if widget.apply_range_filter.get():
            selected_column = widget.selected_column.get()
            min_value, max_value = widget.min_value.get(), widget.max_value.get()

            if selected_column in filtered_data.columns:
                filtered_data = filtered_data[(filtered_data[selected_column] >= min_value) & (filtered_data[selected_column] <= max_value)]
            else:
                messagebox.showerror("Error", f"Column '{selected_column}' not found in dataset.")

        # ✅ Apply modifications dynamically
        if modify_widget.compute_abs_cycle.get():
            filtered_data = self.compute_absolute_cycle(filtered_data)

        if modify_widget.compute_du_dq.get():
            if "Ah-Cyc-Charge-0" in filtered_data.columns and "U[V]" in filtered_data.columns:
                filtered_data["dU/dQ"] = np.gradient(filtered_data["U[V]"], filtered_data["Ah-Cyc-Charge-0"])

        if modify_widget.normalize_voltage.get():
            if "U[V]" in filtered_data.columns:
                max_voltage = filtered_data["U[V]"].max()
                filtered_data["U_normalized"] = filtered_data["U[V]"] / max_voltage

        # ✅ Apply Offset Modification
        if modify_widget.apply_offset.get():
            offset_column = modify_widget.selected_column.get()
            offset_value = modify_widget.offset_value.get()
            if offset_column and offset_column in filtered_data.columns:
                filtered_data[offset_column] += offset_value  # ✅ Modify the column directly

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
        widget = self.app.anode_filter_widget if dataset_type == "anode" else self.app.cathode_filter_widget
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

        # Debugging: Check if the column was added
        print("Modified Dataset Columns:", modified_data.columns)
        print(modified_data.head())


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
        modify_widget = self.app.anode_modify_widget if dataset_type == "anode" else self.app.cathode_modify_widget
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

        # Get the widget for the dataset
        widget = self.app.anode_key_values_widget if dataset_type == "anode" else self.app.cathode_key_values_widget

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

### fit methods

    def compute_linear_spline(self, x, y):
        """
        Computes linear spline fit for given x and y data.
        Returns a dictionary with x and y values for the spline.
        """
        try:
            spline = interp1d(x, y, kind="linear", fill_value="extrapolate")
            x_fit = np.linspace(x.min(), x.max(), 500)  # Generate 500 evenly spaced points for smoothness
            y_fit = spline(x_fit)

            return {"x": x_fit, "y": y_fit}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compute linear spline: {e}")
            return None

### save as .csv and store in data browser - modified and filtered data

    def save_filtered_data(self, dataset_type):
        """
        Saves the filtered data to a user-specified file, with suffixes describing applied filters and modifications.
        """
        filtered_data = self.apply_filters(dataset_type)
        if filtered_data is None:
            return

        dataset_file = self.datasets[dataset_type]["file_path"].get()
        if dataset_file == "No file selected":
            messagebox.showerror("Error", f"No {dataset_type} file loaded.")
            return

        base_filename = os.path.splitext(os.path.basename(dataset_file))[0]
        filter_suffix = self._generate_filter_suffix(dataset_type)
        modification_suffix = self._generate_modification_suffix(dataset_type)
        suggested_filename = f"{base_filename}_{filter_suffix}_{modification_suffix}_filtered.csv"

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
        dataset_name = f"{os.path.splitext(dataset_file)[0]}_{filter_suffix}_{modification_suffix}"

        self.filtered_datasets[dataset_type].append({"name": dataset_name, "data": filtered_data})
        if dataset_type == "anode":
            self.app.anode_browser.add_dataset(dataset_name)
        else:
            self.app.cathode_browser.add_dataset(dataset_name)

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
        filter_widget = (
            self.app.anode_filter_widget if dataset_type == "anode" else self.cathode_filter_widget
        )
        key_values_widget = (
            self.app.anode_key_values_widget if dataset_type == "anode" else self.cathode_key_values_widget
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
                spline_data = self.data_manager.compute_linear_spline(x, y)
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
