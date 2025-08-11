class UIStyling:
    """
    Centralized UI styling configurations.
    """
    
    # General Padding
    PAD_X = 10
    PAD_Y = 10

    # Fonts
    TITLE_FONT = ("Arial", 14, "bold")  # 🔹 Used for app title
    LABEL_FONT = ("Arial", 10)  # 🔹 Used for section titles
    SECTION_FONT = ("Arial", 12, "bold")  # For section headers
    BUTTON_FONT = ("Arial", 9)  # 🔹 Used for all buttons
    DROPDOWN_FONT = ("Arial", 9)  # 🔹 Used for dropdown menus

    FRAME_PADX = 10
    FRAME_PADY = 10

    # Listbox Styling
    LISTBOX_HEIGHT = 10
    LISTBOX_PADX = 5
    LISTBOX_PADY = 5

    # Dropdown Styling
    DROPDOWN_PADX = 5  # padding for dropdowns
    DROPDOWN_POPUP_SIZE = "250x200"  # Width x Height for popup dropdowns

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
