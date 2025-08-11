import tkinter as tk
from tkinter import messagebox

class UIStyling:
    """
    Centralized UI styling configurations.
    """
    FRAME_PADX = 10
    FRAME_PADY = 10
    LABEL_FONT = ("Arial", 10)
    BUTTON_FONT = ("Arial", 9)
    LISTBOX_HEIGHT = 10
    LISTBOX_PADX = 5
    LISTBOX_PADY = 5

class DataWidget:
    """
    Widget for handling file operations and plotting for anode/cathode datasets.
    """
    def __init__(self, parent, label_text, dataset_key, app_context):
        self.app_context = app_context
        self.dataset_key = dataset_key

        self.frame = tk.Frame(parent, relief="groove", borderwidth=2)
        self.frame.grid(pady=UIStyling.FRAME_PADY, padx=UIStyling.FRAME_PADX, row=0, column=0 if dataset_key == "anode" else 1, sticky="nsew")

        # File Operations
        tk.Label(self.frame, text=f"{label_text} file:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.file_label = tk.Label(self.frame, textvariable=self.app_context.datasets[dataset_key]["file_path"], width=40, anchor="w")
        self.file_label.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        tk.Button(self.frame, text="Load", command=self._load_file, font=UIStyling.BUTTON_FONT).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(self.frame, text="Show Data Table", command=self._show_data_table, font=UIStyling.BUTTON_FONT).grid(row=0, column=3, padx=5, pady=5)
        tk.Button(self.frame, text="Plot Data", command=self._plot_data, font=UIStyling.BUTTON_FONT).grid(row=0, column=4, padx=5, pady=5)

    def _load_file(self):
        self.app_context.select_file(self.dataset_key)

    def _show_data_table(self):
        self.app_context.show_data_table(self.dataset_key)

    def _plot_data(self):
        self.app_context.plot_data(self.dataset_key)

class FilteredDataBrowser:
    def __init__(self, parent, label, dataset_type, app_context):
        self.app_context = app_context
        self.dataset_type = dataset_type

        # Create a frame for the browser
        self.frame = tk.LabelFrame(parent, text=label, font=UIStyling.LABEL_FONT)
        self.frame.pack(side="left", fill="both", expand=True, padx=UIStyling.FRAME_PADX, pady=UIStyling.FRAME_PADY)

        # Listbox to show datasets
        self.listbox = tk.Listbox(self.frame, selectmode="multiple", height=UIStyling.LISTBOX_HEIGHT)
        self.listbox.pack(side="left", fill="both", expand=True, padx=UIStyling.LISTBOX_PADX, pady=UIStyling.LISTBOX_PADY)

        # Scrollbar for the listbox
        scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Buttons for functionality
        tk.Button(self.frame, text="Select for Plot", command=self._toggle_selection, font=UIStyling.BUTTON_FONT).pack(pady=5)
        tk.Button(self.frame, text="Show Data Table", command=self._show_data_table, font=UIStyling.BUTTON_FONT).pack(pady=5)

    def _show_data_table(self):
        """
        Display the selected dataset in a new window.
        """
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "No dataset selected.")
            return

        dataset_name = self.listbox.get(selected[0]).replace(" [Selected]", "")
        dataset = self.app_context._get_dataset_by_name(dataset_name, self.dataset_type)

        if dataset is None:
            messagebox.showerror("Error", "Failed to retrieve the selected dataset.")
            return

        self._display_dataset_table(dataset, dataset_name)

    def _display_dataset_table(self, dataset, dataset_name):
        """
        Helper function to display a dataset in a new window.
        """
        table_window = tk.Toplevel(self.app_context.root)
        table_window.title(f"Data Table - {dataset_name}")
        table_window.geometry("800x600")

        x_scrollbar = tk.Scrollbar(table_window, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")

        y_scrollbar = tk.Scrollbar(table_window, orient="vertical")
        y_scrollbar.pack(side="right", fill="y")

        text = tk.Text(table_window, wrap="none", xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
        text.pack(side="left", fill="both", expand=True)

        x_scrollbar.config(command=text.xview)
        y_scrollbar.config(command=text.yview)

        # Insert the dataset as a string
        text.insert("1.0", dataset.to_string(index=False))

    def add_dataset(self, dataset_name):
        """
        Add a dataset to the browser.
        """
        self.listbox.insert(tk.END, dataset_name)

    def get_selected_datasets(self):
        """
        Get the selected datasets from the browser.
        """
        return [
            self.listbox.get(idx).replace(" [Selected]", "")
            for idx in range(self.listbox.size())
            if self.listbox.get(idx).endswith("[Selected]")
        ]

    def clear_browser(self):
        """
        Clear all datasets from the browser.
        """
        self.listbox.delete(0, tk.END)

    def _toggle_selection(self):
        """
        Mark or unmark the selected datasets as [Selected].
        """
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "No datasets selected.")
            return

        for idx in selected_indices:
            item = self.listbox.get(idx)
            if "[Selected]" in item:
                # Remove the [Selected] tag
                self.listbox.delete(idx)
                self.listbox.insert(idx, item.replace(" [Selected]", ""))
                self.listbox.itemconfig(idx, {"fg": "black"})
            else:
                # Add the [Selected] tag
                self.listbox.delete(idx)
                self.listbox.insert(idx, f"{item} [Selected]")
                self.listbox.itemconfig(idx, {"fg": "green"})
