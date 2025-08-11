import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt


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
