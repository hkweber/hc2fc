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
    DROPDOWN_FONT = ("Arial", 9)  # centralized dropdown font
    DROPDOWN_PADX = 5  # padding for dropdowns

    # Plot Styling
    PLOT_FIGSIZE = (10, 6)
    PLOT_LEGEND_FONT = "small"
    PLOT_GRID = True
    COLOR_PALETTE = {
        "anode": "blue",
        "cathode": "red",
        "full_cell": "purple",
        "default": "black"
    }