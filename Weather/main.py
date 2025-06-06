"""
перед запуском программы нужно установить библиотеки: pip install -r requirements.txt
"""


import tkinter as tk
import asyncio
from constants import THEMES
from data_manager import load_favorite_cities, save_favorite_cities, load_settings, save_settings_to_file
from weather_api import get_city_by_ip, get_weather_data_async
from ui_components import check_weather_warning, show_hourly_and_daily_forecast
from splash_screen import SplashScreen

# Global variables
cached_forecast = None
cached_city = None
is_dark_theme = False
theme = "light"
auto_update_enabled = False
edit_mode = False

def on_refresh_click():
    city = city_entry.get()
    if city:
        asyncio.run_coroutine_threadsafe(async_show_weather(city), loop)

def remove_city_from_favorites(city):
    if city in favorite_cities:
        favorite_cities.remove(city)
        save_favorite_cities(favorite_cities)
        update_favorites_menu()

def move_city_up(index):
    if index > 0:
        favorite_cities[index], favorite_cities[index-1] = favorite_cities[index-1], favorite_cities[index]
        save_favorite_cities(favorite_cities)
        update_favorites_menu()

def move_city_down(index):
    if index < len(favorite_cities) - 1:
        favorite_cities[index], favorite_cities[index+1] = favorite_cities[index+1], favorite_cities[index]
        save_favorite_cities(favorite_cities)
        update_favorites_menu()

def on_update_button_click(city):
    asyncio.ensure_future(async_show_weather(city))

def update_favorites_menu():
    for widget in favorites_frame.winfo_children():
        widget.destroy()
    for i, city in enumerate(favorite_cities):
        city_frame = tk.Frame(favorites_frame, bg=THEMES["light"]["bg"] if not is_dark_theme else THEMES["dark"]["bg"])
        city_frame.pack(side=tk.LEFT, padx=5, pady=5)

        city_label = tk.Label(city_frame, text=city, font=('Arial', 10),
                              bg=THEMES["light"]["primary"] if not is_dark_theme else THEMES["dark"]["primary"],
                              fg=THEMES["light"]["secondary"] if not is_dark_theme else THEMES["dark"]["secondary"])
        city_label.pack(side=tk.LEFT)

        if edit_mode:
            # Кнопка удаления
            del_btn = tk.Button(city_frame, text="✖", font=('Arial', 10),
                                bg="#e74c3c", fg="white", padx=3,
                                command=lambda c=city: remove_city_from_favorites(c))
            del_btn.pack(side=tk.LEFT, padx=(5, 0))

            # Кнопка вверх
            up_btn = tk.Button(city_frame, text="←", font=('Arial', 10),
                               bg=THEMES["light"]["primary"] if not is_dark_theme else THEMES["dark"]["primary"],
                               fg=THEMES["light"]["secondary"] if not is_dark_theme else THEMES["dark"]["secondary"],
                               padx=3,
                               command=lambda idx=i: move_city_up(idx))
            up_btn.pack(side=tk.LEFT, padx=(5, 0))

            # Кнопка вниз
            down_btn = tk.Button(city_frame, text="→", font=('Arial', 10),
                                 bg=THEMES["light"]["primary"] if not is_dark_theme else THEMES["dark"]["primary"],
                                 fg=THEMES["light"]["secondary"] if not is_dark_theme else THEMES["dark"]["secondary"],
                                 padx=3,
                                 command=lambda idx=i: move_city_down(idx))
            down_btn.pack(side=tk.LEFT, padx=(5, 0))
        else:
            # По клику показываем погоду
            city_label.bind("<Button-1>", lambda e, c=city: on_city_click(c))

def on_city_click(city):
    asyncio.ensure_future(async_show_weather(city))

def add_city_to_favorites():
    city = city_entry.get()
    if city and city not in favorite_cities:
        favorite_cities.append(city)
        save_favorite_cities(favorite_cities)
        update_favorites_menu()

async def async_show_weather(city):
    result = await get_weather_data_async(city)
    if result == "not_found" or result is None:
        update_ui_with_weather(city, "not_found")
    else:
        update_ui_with_weather(city, result)

def update_ui_with_weather(city, result):
    clear_frame()
    if result == "not_found":
        show_error('Город не найден!')
    else:
        global cached_city, cached_forecast
        cached_city = city
        cached_forecast = result
        check_weather_warning(result, weather_warning_label)
        show_hourly_and_daily_forecast(frame, city, *result, is_dark_theme)

def clear_frame():
    error_label.config(text="")
    for widget in frame.winfo_children():
        widget.destroy()

def show_error(message):
    error_label.config(text=message, fg=THEMES["dark"]["error"] if is_dark_theme else THEMES["light"]["error"])

def toggle_theme():
    global theme, is_dark_theme
    is_dark_theme = not is_dark_theme
    theme = "dark" if is_dark_theme else "light"
    apply_theme()
    save_settings_to_file(auto_update_enabled, auto_update_interval // 60000, theme)
    # Если уже есть показанный прогноз — обновим отображение
    if cached_forecast and cached_city:
        clear_frame()
        show_hourly_and_daily_forecast(frame, cached_city, *cached_forecast, is_dark_theme)

def open_settings_window():
    def save_settings():
        nonlocal interval_var, theme_var, enabled_var
        global auto_update_enabled, auto_update_interval, theme, is_dark_theme

        auto_update_enabled = enabled_var.get()
        selected = interval_var.get()
        auto_update_interval = int(selected) * 60 * 1000

        theme = theme_var.get()
        is_dark_theme = (theme == "dark")
        apply_theme()

        save_settings_to_file(auto_update_enabled, selected, theme)
        settings_window.destroy()
        if auto_update_enabled:
            root.after(100, auto_update_weather)

    settings_window = tk.Toplevel(root)
    settings_window.title("Настройки")
    settings_window.geometry("300x250")
    settings_window.configure(bg=THEMES["light"]["bg"] if not is_dark_theme else THEMES["dark"]["bg"])

    bg = THEMES["light"]["bg"] if not is_dark_theme else THEMES["dark"]["bg"]
    fg = THEMES["light"]["text"] if not is_dark_theme else THEMES["dark"]["text"]

    enabled_var = tk.BooleanVar(value=auto_update_enabled)
    interval_var = tk.StringVar(value=str(int(auto_update_interval) // (60 * 1000)))
    theme_var = tk.StringVar(value=theme)

    tk.Checkbutton(settings_window, text="Включить автообновление", variable=enabled_var,
                   bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
                   font=('Arial', 12)).pack(pady=10)

    tk.Label(settings_window, text="Интервал (минут):", bg=bg, fg=fg, font=('Arial', 12)).pack()
    interval_menu = tk.OptionMenu(settings_window, interval_var, "5", "15", "30", "60")
    interval_menu.configure(bg=bg, fg=fg, font=('Arial', 12))
    interval_menu.pack(pady=10)

    tk.Label(settings_window, text="Тема:", bg=bg, fg=fg, font=('Arial', 12)).pack()
    tk.Radiobutton(settings_window, text="Светлая", variable=theme_var, value="light",
                   bg=bg, fg=fg, font=('Arial', 12), selectcolor=bg).pack()
    tk.Radiobutton(settings_window, text="Тёмная", variable=theme_var, value="dark",
                   bg=bg, fg=fg, font=('Arial', 12), selectcolor=bg).pack()

    tk.Button(settings_window, text="Сохранить", command=save_settings,
              bg=bg, fg=fg, font=('Arial', 12)).pack(pady=10)

def auto_update_weather():
    if auto_update_enabled:
        current_city = city_entry.get()
        if current_city:
            asyncio.run_coroutine_threadsafe(async_show_weather(current_city), loop)
        root.after(auto_update_interval, auto_update_weather)

def apply_theme():
    colors = THEMES[theme]
    
    # Update main containers
    root.configure(bg=colors["bg"])
    main_container.configure(bg=colors["bg"])
    search_frame.configure(bg=colors["bg"])
    favorites_section.configure(bg=colors["bg"])
    weather_frame.configure(bg=colors["bg"])
    frame.configure(bg=colors["bg"])
    
    # Update entry styling
    city_entry.configure(
        bg=colors["secondary"],
        fg=colors["text"],
        insertbackground=colors["text"]  # Цвет курсора
    )
    
    # Update button styling
    button_style = {
        'bg': colors["primary"],
        'fg': colors["secondary"],
        'activebackground': colors["accent"],  # Цвет при наведении
        'activeforeground': colors["secondary"]
    }
    
    for button in [refresh_button, settings_button, add_fav_button, edit_button]:
        button.configure(**button_style)
    
    # Update label styling
    error_label.configure(bg=colors["bg"], fg=colors["error"])
    weather_warning_label.configure(bg=colors["bg"], fg=colors["accent"])
    favorites_label.configure(bg=colors["bg"], fg=colors["text"])
    
    # Update favorites frame and its children
    favorites_frame.configure(bg=colors["bg"])
    
    # Update all widgets in favorites frame
    for widget in favorites_frame.winfo_children():
        if isinstance(widget, tk.Frame):
            widget.configure(bg=colors["bg"])
            for child in widget.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(
                        bg=colors["primary"],
                        fg=colors["secondary"]
                    )
                elif isinstance(child, tk.Button):
                    child.configure(
                        bg=colors["primary"],
                        fg=colors["secondary"],
                        activebackground=colors["accent"],
                        activeforeground=colors["secondary"]
                    )
    
    # Update weather display frame and its children
    for widget in frame.winfo_children():
        if isinstance(widget, tk.Frame):
            widget.configure(bg=colors["bg"])
            for child in widget.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(
                        bg=colors["bg"],
                        fg=colors["text"]
                    )
                elif isinstance(child, tk.Frame):
                    child.configure(bg=colors["bg"])
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, tk.Label):
                            grandchild.configure(
                                bg=colors["secondary"],
                                fg=colors["text"]
                            )
    
    # Update favorites menu
    update_favorites_menu()
    
    # Если есть кэшированный прогноз, обновим его отображение
    if cached_forecast and cached_city:
        clear_frame()
        show_hourly_and_daily_forecast(frame, cached_city, *cached_forecast, is_dark_theme)

def toggle_edit_mode():
    global edit_mode
    edit_mode = not edit_mode
    update_favorites_menu()
    edit_button.config(text="Готово" if edit_mode else "Редактировать")

# Initialize the application
root = tk.Tk()
root.geometry("1000x900+400+50")
root.title("Погода")
root.configure(bg=THEMES["light"]["bg"])

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def process_asyncio_events():
    loop.call_soon(loop.stop)
    loop.run_forever()
    root.after(50, process_asyncio_events)

root.after(50, process_asyncio_events)

# Create main container with padding
main_container = tk.Frame(root, bg=THEMES["light"]["bg"], padx=20, pady=20)
main_container.pack(fill=tk.BOTH, expand=True)

# Create search frame
search_frame = tk.Frame(main_container, bg=THEMES["light"]["bg"])
search_frame.pack(fill=tk.X, pady=(0, 20))

# Create city entry with modern styling
city_entry = tk.Entry(search_frame, width=30, font=('Segoe UI', 14),
                     bg=THEMES["light"]["secondary"], fg=THEMES["light"]["text"],
                     borderwidth=1, relief='solid')
city_entry.pack(side=tk.LEFT, padx=(0, 10))

# Create buttons with modern styling
button_style = {
    'font': ('Segoe UI', 12),
    'bg': THEMES["light"]["primary"],
    'fg': THEMES["light"]["secondary"],
    'borderwidth': 0,
    'padx': 15,
    'pady': 8,
    'cursor': 'hand2'
}

refresh_button = tk.Button(search_frame, text="Обновить прогноз", command=on_refresh_click, **button_style)
refresh_button.pack(side=tk.LEFT, padx=5)

settings_button = tk.Button(search_frame, text="Настройки", command=open_settings_window, **button_style)
settings_button.pack(side=tk.LEFT, padx=5)

add_fav_button = tk.Button(search_frame, text="☆ В избранное", command=add_city_to_favorites, **button_style)
add_fav_button.pack(side=tk.LEFT, padx=5)

# Create favorites section with modern styling
favorites_section = tk.Frame(main_container, bg=THEMES["light"]["bg"])
favorites_section.pack(fill=tk.X, pady=(0, 20))

favorites_label = tk.Label(favorites_section, text="Избранные города:", 
                          font=('Segoe UI', 12, 'bold'),
                          bg=THEMES["light"]["bg"],
                          fg=THEMES["light"]["text"])
favorites_label.pack(anchor=tk.W, pady=(0, 10))

favorites_frame = tk.Frame(favorites_section, bg=THEMES["light"]["bg"])
favorites_frame.pack(fill=tk.X)

edit_button = tk.Button(favorites_section, text="Редактировать", command=toggle_edit_mode,
                       **button_style)
edit_button.pack(anchor=tk.E, pady=(10, 0))

# Create weather display section
weather_frame = tk.Frame(main_container, bg=THEMES["light"]["bg"])
weather_frame.pack(fill=tk.BOTH, expand=True)

error_label = tk.Label(weather_frame, text="", font=('Segoe UI', 12),
                      bg=THEMES["light"]["bg"], fg=THEMES["light"]["error"])
error_label.pack(pady=10)

weather_warning_label = tk.Label(weather_frame, text="", font=('Segoe UI', 12, 'bold'),
                               bg=THEMES["light"]["bg"], fg=THEMES["light"]["accent"])
weather_warning_label.pack(pady=10)

frame = tk.Frame(weather_frame, bg=THEMES["light"]["bg"])
frame.pack(fill=tk.BOTH, expand=True)

# Load initial data
favorite_cities = load_favorite_cities()
settings = load_settings()
auto_update_enabled = settings["auto_update_enabled"]
auto_update_interval = settings["auto_update_interval"]
theme = settings["theme"]
is_dark_theme = (theme == "dark")

# Hide window initially
root.withdraw()

# Create splash screen
splash = SplashScreen(root, 
                     bg=THEMES["light"]["bg"] if not is_dark_theme else THEMES["dark"]["bg"],
                     fg=THEMES["light"]["text"] if not is_dark_theme else THEMES["dark"]["text"])

async def init_app():
    apply_theme()
    default_city = await get_city_by_ip()
    if default_city:
        await async_show_weather(default_city)
    splash.destroy()  # Закрываем окно загрузки
    root.deiconify()  # Показываем основное окно

# Start the application
asyncio.run_coroutine_threadsafe(init_app(), loop)
update_favorites_menu()

if auto_update_enabled:
    auto_update_weather()

# Configure grid weights
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)

# Start the main loop
root.mainloop() 
