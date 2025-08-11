import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import numpy as np


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

    # other methods

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
                filtered_data = self.app.step_change_filter(filtered_data, step_column)
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
            filtered_data = self.app.compute_absolute_cycle(filtered_data)

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
