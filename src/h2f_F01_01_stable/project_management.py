### project_management.py

import os
import zipfile
import json
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class ProjectManager:
    """
    Manages saving and loading of hc2fc projects, including datasets, filters, and plots.
    """

    def __init__(self, app_context):
        self.app = app_context  # Reference to HC2FCApp instance
        self.loaded_plots = []  # Store loaded plots separately

    # =====================
    #  Project Save Logic
    # =====================

    def save_project_callback(self):
        """ Opens a file dialog for saving a project. """
        save_folder = os.path.join(os.getcwd(), "projects")
        os.makedirs(save_folder, exist_ok=True)

        file_path = filedialog.asksaveasfilename(
            defaultextension=".hc2fcproj",
            filetypes=[("HC2FC Project Files", "*.hc2fcproj"), ("All Files", "*.*")],
            title="Save Project",
            initialdir=save_folder
        )

        if file_path:
            self.save_project(file_path)

    def save_project(self, project_path):
        """ Saves project data into a ZIP file. """
        try:
            project_data = {
                "original_files": {
                    "anode": self.app.data_manager.datasets["anode"]["file_path"].get(),
                    "cathode": self.app.data_manager.datasets["cathode"]["file_path"].get()
                },
                "datasets": {},
                "filters": {},
                "plots": []
            }

            # ✅ Store filtered datasets
            for dataset_type, datasets in self.app.data_manager.filtered_datasets.items():
                project_data["datasets"][dataset_type] = [dataset["name"] for dataset in datasets]

            # ✅ Save filter settings
            for dataset_type in ["anode", "cathode"]:
                widget = self.app.anode_filter_widget if dataset_type == "anode" else self.app.cathode_filter_widget
                project_data["filters"][dataset_type] = {
                    "remove_pause": widget.remove_pause.get(),
                    "select_cycle": widget.select_cycle.get(),
                    "selected_cycle": widget.cycle_selection.get(),
                    "plot_type": widget.plot_option.get()
                }

            # ✅ Save project metadata & datasets into a ZIP file
            with zipfile.ZipFile(project_path, "w", zipfile.ZIP_DEFLATED) as project_zip:
                project_zip.writestr("project_metadata.json", json.dumps(project_data, indent=4))

                # ✅ Step 3: Update UI file paths for anode/cathode main datasets
                if self.app.data_manager.datasets["anode"]["data"] is not None:
                    filename = self.app.data_manager.datasets["anode"]["file_path"].get()
                    self.app.anode_widget.file_label.config(text=f"Anode file: {filename}")

                if self.app.data_manager.datasets["cathode"]["data"] is not None:
                    filename = self.app.data_manager.datasets["cathode"]["file_path"].get()
                    self.app.cathode_widget.file_label.config(text=f"Cathode file: {filename}")

                # ✅ Ensure Tkinter refreshes the UI
                self.app.root.update_idletasks()


                # Save filtered datasets
                for dataset_type, datasets in self.app.data_manager.filtered_datasets.items():
                    for dataset in datasets:
                        dataset_csv = dataset["data"].to_csv(index=False)
                        project_zip.writestr(f"datasets/{dataset['name']}.csv", dataset_csv)

            print(f"✅ Project saved at: {project_path}")

        except Exception as e:
            print(f"❌ Error saving project: {e}")

    # =====================
    #  Project Load Logic
    # =====================

    def load_project_callback(self):
        """ Opens a file dialog for selecting a project to load. """
        file_path = filedialog.askopenfilename(
            filetypes=[("HC2FC Project Files", "*.hc2fcproj"), ("All Files", "*.*")],
            title="Load Project"
        )

        if file_path:
            self.load_project(file_path)

    def load_project(self, project_path):
        """ Loads a project from a ZIP file. """
        try:
            with zipfile.ZipFile(project_path, "r") as project_zip:
                if "project_metadata.json" not in project_zip.namelist():
                    print("❌ Error: Missing project metadata.")
                    return
                
                # ✅ Read metadata
                metadata_json = project_zip.read("project_metadata.json").decode()
                project_data = json.loads(metadata_json)

                # ✅ Clear existing data
                self.app.data_manager.datasets = {
                    "anode": {"data": None, "file_path": tk.StringVar(value="No file selected")},
                    "cathode": {"data": None, "file_path": tk.StringVar(value="No file selected")}
                }
                self.app.data_manager.filtered_datasets = {"anode": [], "cathode": [], "full_cell": []}
                self.app.data_manager.modified_datasets = {"anode": None, "cathode": None}

                # ✅ Load original datasets using filenames from project_metadata.json
                for dataset_type in ["anode", "cathode"]:
                    original_filename = project_data["original_files"].get(dataset_type, "")
                    
                    if original_filename and f"datasets/{original_filename}" in project_zip.namelist():
                        with project_zip.open(f"datasets/{original_filename}") as dataset_file:
                            dataset_df = pd.read_csv(dataset_file)
                            self.app.data_manager.datasets[dataset_type]["data"] = dataset_df
                            self.app.data_manager.datasets[dataset_type]["file_path"].set(original_filename)  # ✅ Update file path

                    else:
                        print(f"⚠️ Warning: Original {dataset_type} dataset '{original_filename}' not found in project.")

                # ✅ Restore filtered datasets
                for dataset_type, dataset_list in project_data["datasets"].items():
                    for dataset_name in dataset_list:
                        dataset_csv_path = f"datasets/{dataset_name}.csv"
                        if dataset_csv_path in project_zip.namelist():
                            with project_zip.open(dataset_csv_path) as dataset_file:
                                dataset_df = pd.read_csv(dataset_file)
                                
                                self.app.data_manager.filtered_datasets[dataset_type].append(
                                    {"name": dataset_name, "data": dataset_df}
                                )

                # ✅ Restore UI for datasets
                for dataset in self.app.data_manager.filtered_datasets["anode"]:
                    self.app.anode_browser.add_dataset(dataset["name"])
                for dataset in self.app.data_manager.filtered_datasets["cathode"]:
                    self.app.cathode_browser.add_dataset(dataset["name"])
                for dataset in self.app.data_manager.filtered_datasets["full_cell"]:
                    self.app.full_cell_browser.add_dataset(dataset["name"])



                # ✅ Step 3: Update UI file paths for anode/cathode main datasets
                if self.app.data_manager.datasets["anode"]["data"] is not None:
                    self.app.anode_widget.file_label.config(text=self.app.data_manager.datasets["anode"]["file_path"].get())
                    self.app.anode_widget.file_path.set(self.app.data_manager.datasets["anode"]["file_path"].get())  # ✅ Update UI variable

                if self.app.data_manager.datasets["cathode"]["data"] is not None:
                    self.app.cathode_widget.file_label.config(text=self.app.data_manager.datasets["cathode"]["file_path"].get())
                    self.app.cathode_widget.file_path.set(self.app.data_manager.datasets["cathode"]["file_path"].get())  # ✅ Update UI variable

                # ✅ Ensure Tkinter refreshes the UI
                self.app.root.update_idletasks()

                # ✅ Force a full UI refresh after loading
                self.app.root.update_idletasks()

                print("✅ Datasets successfully restored in UI.")

                # ✅ Step 4: Restore filter settings
                for dataset_type in ["anode", "cathode"]:
                    widget = self.app.anode_filter_widget if dataset_type == "anode" else self.app.cathode_filter_widget
                    if dataset_type in project_data["filters"]:
                        filter_data = project_data["filters"][dataset_type]
                        widget.remove_pause.set(filter_data.get("remove_pause", False))
                        widget.select_cycle.set(filter_data.get("select_cycle", False))
                        widget.cycle_selection.set(filter_data.get("selected_cycle", "All"))
                        widget.plot_option.set(filter_data.get("plot_type", "U-t"))

                print("✅ Filters successfully restored.")

                print("🎉 Project loaded successfully!")

        except Exception as e:
            print(f"❌ Error loading project: {e}")


    # =====================
    #  Restoring Plots
    # =====================

    def show_loaded_plots(self):
        """ Displays restored plots in separate windows. """
        if not self.loaded_plots:
            messagebox.showerror("Error", "No plots were loaded from the project file.")
            return

        for i, image in enumerate(self.loaded_plots):
            plot_window = tk.Toplevel(self.app.root)
            plot_window.title(f"Restored Plot {i+1}")
            plot_window.geometry("600x400")

            img_tk = ImageTk.PhotoImage(image)
            label = tk.Label(plot_window, image=img_tk)
            label.image = img_tk  # Keep reference to avoid garbage collection
            label.pack()

        print("Displayed loaded plots.")

