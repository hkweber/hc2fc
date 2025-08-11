### ui_elements.py


import tkinter as tk
from ui_styles import UIStyling

    
class UIElements():
    """
    A helper class to create styled UI elements for Tkinter.
    """
    @staticmethod
    def section_frame(parent, section_name):
        """ Creates a named section frame"""
        section_frame = tk.LabelFrame(parent, text=section_name, font=UIStyling.LABEL_FONT)
        section_frame.pack(fill="x", padx=UIStyling.PAD_X, pady=UIStyling.PAD_Y)
        return section_frame
    
    @staticmethod
    def frame(parent):
        """ Creates a named section frame"""
        frame = tk.Frame(parent)
        frame.pack(anchor="w", padx=UIStyling.PAD_X, pady=UIStyling.PAD_Y)
        return frame
    
    @staticmethod
    def button(parent, text, command):
        """ Creates a style tk.button section frame"""
        button = tk.Button(parent, text=text,
                command=command,
                font=UIStyling.BUTTON_FONT).pack(side="left", padx=UIStyling.PAD_X)
        return button
    
    @staticmethod
    def label(parent, text):
        """ Creates a style tk.button section frame"""
        label = tk.Label(parent, text=text,
                font=UIStyling.LABEL_FONT).pack(side="left", padx=5)
        return label
    
    @staticmethod
    def checkbutton(parent, text, variable):
        """ Creates a style tk.button section frame"""
        checkbutton = tk.Checkbutton(parent, text=text, variable=variable,
                font=UIStyling.LABEL_FONT).pack(anchor="w",padx=5)
        return checkbutton
    
    @staticmethod
    def radiobutton(parent, text, variable, command, value = ""):
        """ Creates a style tk.button section frame"""

        radiobutton = tk.Radiobutton(parent, text=text, variable=variable, value="no fit",
                       font=UIStyling.BUTTON_FONT, command=command)
        radiobutton.pack(anchor="w", padx=UIStyling.LISTBOX_PADX)
        return radiobutton
    
    @staticmethod
    def dropdown(parent, variable):
        """ Creates a style tk.button section frame"""
        dropdown = tk.OptionMenu(parent, variable=variable, value=value)
        dropdown.config(font=UIStyling.DROPDOWN_FONT, state="disabled")
        dropdown.pack(side="left", padx=UIStyling.DROPDOWN_PADX)
        return dropdown
    


