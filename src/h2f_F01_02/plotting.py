from tkinter import messagebox, Toplevel, Listbox, Scrollbar
import tkinter as tk
import matplotlib.pyplot as plt
from styles import UIStyling  # Import centralized styling

class MultiGraphPlotter:
    def __init__(self, app_context):
        self.app_context = app_context
        self.color_palette = UIStyling.COLOR_PALETTE  # Use centralized color palette

        # Initialize the plot selection variable
        self.multi_graph_plot_option = tk.StringVar(value="U-t (Voltage-Time)")

    def open_plot_selection(self):
        """
        Opens a scrollable popup to select a plot type.
        """
        popup = Toplevel(self.app_context.root)
        popup.title("Select Plot Type")
        popup.geometry(UIStyling.DROPDOWN_POPUP_SIZE)  # Use centralized size

        scrollbar = Scrollbar(popup)
        scrollbar.pack(side="right", fill="y")

        listbox = Listbox(popup, yscrollcommand=scrollbar.set, font=UIStyling.DROPDOWN_FONT)
        listbox.pack(fill="both", expand=True)

        plot_options = ["U-t (Voltage-Time)", "I-t (Current-Time)", "Q-U (Charge-Voltage)"]
        for option in plot_options:
            listbox.insert("end", option)

        def select_option(event):
            selected = listbox.get(listbox.curselection())
            self.multi_graph_plot_option.set(selected)
            popup.destroy()

        listbox.bind("<Double-Button-1>", select_option)

    def create_ui(self, parent):
        """
        Create the UI elements for the plot selection inside the given parent frame.
        """
        multi_graph_frame = tk.Frame(parent)
        multi_graph_frame.pack(pady=UIStyling.FRAME_PADY, padx=UIStyling.FRAME_PADX, fill="x")

        tk.Label(multi_graph_frame, text="Select Plot Type:", font=UIStyling.LABEL_FONT).pack(side="left", padx=UIStyling.DROPDOWN_PADX)

        self.plot_selection_button = tk.Button(
            multi_graph_frame, textvariable=self.multi_graph_plot_option, 
            command=self.open_plot_selection, font=UIStyling.BUTTON_FONT
        )
        self.plot_selection_button.pack(side="left", padx=UIStyling.DROPDOWN_PADX)

        # Plot Multi-Graph Button
        tk.Button(multi_graph_frame, text="Plot Multi-Graph", command=self.plot_multi_graph, font=UIStyling.BUTTON_FONT).pack(side="left", padx=UIStyling.PAD_X)

    def plot_multi_graph(self):
        """
        Fetch selected datasets from anode, cathode, and full cell browsers
        and plot them in a single figure.
        """
        # Get selected datasets from all three browsers
        datasets = {
            "anode": self.app_context.data_browsers["anode"].get_selected_datasets(),
            "cathode": self.app_context.data_browsers["cathode"].get_selected_datasets(),
            "full_cell": self.app_context.data_browsers["full_cell"].get_selected_datasets()
        }

        # Check if at least one dataset is selected
        if not any(datasets.values()):
            messagebox.showerror("Error", "No datasets selected from any browser.")
            return

        # Create the main figure
        fig, ax1 = plt.subplots(figsize=UIStyling.PLOT_FIGSIZE)

        # Prepare a secondary x-axis for Q-U plots
        ax2 = ax1.twiny() if self.multi_graph_plot_option.get() == "Q-U (Charge-Voltage)" else None

        # Plot datasets directly
        for dataset_type, dataset_names in datasets.items():
            for dataset_name in dataset_names:
                dataset = self.app_context.multi_data_processor.get_dataset_by_name(dataset_name, dataset_type)
                if dataset is not None:
                    self._plot_dataset(ax1, ax2, dataset, dataset_name, dataset_type)

        # Update labels dynamically based on plot type
        xlabel, ylabel = self._get_axis_labels(self.multi_graph_plot_option.get())
        ax1.set_xlabel(xlabel)
        ax1.set_ylabel(ylabel)
        ax1.set_title("Multi-Graph Plot")

        # Adjust the legend to avoid overlapping with the graph
        ax1.legend(loc="best", fontsize=UIStyling.PLOT_LEGEND_FONT)
        plt.tight_layout()
        plt.grid(UIStyling.PLOT_GRID)
        plt.show()

    def _plot_dataset(self, ax1, ax2, dataset, label, dataset_type):
        """
        Plot a single dataset on the current matplotlib figure based on the selected plot type.
        """
        plot_type = self.multi_graph_plot_option.get()
        color = self.color_palette.get(dataset_type, UIStyling.COLOR_PALETTE["default"])

        try:
            if plot_type == "U-t (Voltage-Time)":
                ax1.plot(dataset["Time[h]"], dataset["U[V]"], label=label, color=color)
            elif plot_type == "I-t (Current-Time)":
                ax1.plot(dataset["Time[h]"], dataset["I[A]"], label=label, color=color)
            elif plot_type == "Q-U (Charge-Voltage)":
                self._plot_qu_dataset(ax1, ax2, dataset, label, color)
            else:
                messagebox.showerror("Error", f"Unsupported plot type: {plot_type}")
        except KeyError as e:
            messagebox.showerror("Error", f"Missing required columns in dataset {label}: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to plot dataset {label}: {e}")

    def _plot_qu_dataset(self, ax1, ax2, dataset, label, color):
        """
        Plot a dataset for Q-U (Charge-Voltage) visualization.
        """
        if "Ah-Cyc-Charge-0" not in dataset.columns or "Ah-Cyc-Discharge-0" not in dataset.columns:
            messagebox.showerror("Error", f"Dataset {label} is missing required columns for Q-U plotting.")
            return

        charge_data = dataset[dataset["Command"].str.contains("Charge", na=False)]
        discharge_data = dataset[dataset["Command"].str.contains("Discharge", na=False)]

        if not charge_data.empty:
            ax1.plot(charge_data["Ah-Cyc-Charge-0"], charge_data["U[V]"], label=f"{label} (Charge)", color=color)
            ax1.set_xlabel("Charge (Ah)")

        if ax2 and not discharge_data.empty:
            ax2.plot(discharge_data["Ah-Cyc-Discharge-0"], discharge_data["U[V]"], label=f"{label} (Discharge)", color=color, linestyle="--")
            ax2.set_xlabel("Discharge (Ah)")

    def _get_axis_labels(self, plot_type):
        """
        Returns appropriate axis labels based on the selected plot type.
        """
        return {
            "U-t (Voltage-Time)": ("Time (h)", "Voltage (V)"),
            "I-t (Current-Time)": ("Time (h)", "Current (A)"),
            "Q-U (Charge-Voltage)": ("Charge/Discharge (Ah)", "Voltage (V)")
        }.get(plot_type, ("X-axis", "Y-axis"))
