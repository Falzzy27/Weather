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

        save_settings_to_file(auto_update_enabled, selected)
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