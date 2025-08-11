from tkinter import messagebox
import matplotlib.pyplot as plt

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
