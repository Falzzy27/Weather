import tkinter as tk

# Theme configurations
THEMES = {
    "light": {
        "bg": "#ffffff",
        "text": "#000000"
    },
    "dark": {
        "bg": "#2b2b2b",
        "text": "#ffffff"
    }
}

def apply_theme():
    """Apply the current theme to the application"""
    global is_dark_theme
    current_theme = THEMES["dark"] if is_dark_theme else THEMES["light"]
    return current_theme["bg"], current_theme["text"]

def get_theme_colors():
    """Get current theme colors"""
    return apply_theme() 