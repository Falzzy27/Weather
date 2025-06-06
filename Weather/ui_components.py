import tkinter as tk
from PIL import Image, ImageTk
from constants import THEMES

def fade_in_icon(label, img, steps=30, delay=20):
    def step(alpha):
        img_resized = img.resize((40 + alpha // 2, 40 + alpha // 2), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img_resized)
        label.configure(image=photo)
        label.image = photo
        if alpha < steps:
            label.after(delay, lambda: step(alpha + 1))

    step(0)

def check_weather_warning(result, weather_warning_label):
    weather_warning_label.config(text="")
    hourly_forecast, daily_forecast = result

    # Проверка на экстремальные температуры
    temperatures = [temp for _, temp, _ in hourly_forecast]
    min_temp = min(temperatures)
    max_temp = max(temperatures)

    if max_temp > 35:
        weather_warning_label.config(text="⚠️ Внимание: Ожидается сильная жара! Берегитесь перегрева.", fg=THEMES["light"]["error"])
    elif min_temp < -10:
        weather_warning_label.config(text="❄️ Внимание: Очень холодная погода. Оденьтесь тепло.", fg=THEMES["light"]["accent"])
    else:
        weather_warning_label.config(text="✅ Погода стабильная и комфортная.", fg=THEMES["light"]["accent"])

    # Проверка на осадки или неблагоприятные погодные условия
    for status, _ in daily_forecast:
        if "дождь" in status or "снег" in status:
            weather_warning_label.config(text="🌧️ Внимание: Ожидаются осадки. Не забудьте зонт!", fg=THEMES["light"]["accent"])

def show_hourly_and_daily_forecast(frame, city, hourly, daily, is_dark_theme):
    colors = THEMES["dark"] if is_dark_theme else THEMES["light"]
    
    # Создаем контейнер для часового прогноза
    hourly_container = tk.Frame(frame, bg=colors["bg"], padx=20, pady=20)
    hourly_container.pack(fill=tk.X, pady=(0, 20))
    
    # Заголовок часового прогноза
    title = tk.Label(hourly_container, 
                    text=f"Погода по часам: {city}", 
                    font=('Segoe UI', 16, 'bold'),
                    bg=colors["bg"],
                    fg=colors["text"])
    title.pack(pady=(0, 20))

    # Контейнер для карточек с погодой
    cards_frame = tk.Frame(hourly_container, bg=colors["bg"])
    cards_frame.pack(fill=tk.X)

    # Настройка веса колонок для равномерного распределения
    for i in range(8):
        cards_frame.grid_columnconfigure(i, weight=1, uniform="equal")

    for i, (time, temp, icon_path) in enumerate(hourly):
        # Создаем карточку для каждого часа
        card = tk.Frame(cards_frame,
                       bg=colors["secondary"],
                       padx=10,
                       pady=15,
                       relief="flat",
                       borderwidth=1)
        card.grid(row=0, column=i, padx=5, sticky="nsew")

        # Время
        time_label = tk.Label(card,
                            text=time,
                            font=('Segoe UI', 12),
                            bg=colors["secondary"],
                            fg=colors["text"])
        time_label.pack(pady=(0, 10))

        # Иконка погоды
        img = icon_path.resize((40, 40), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        icon_label = tk.Label(card,
                            image=photo,
                            bg=colors["secondary"])
        icon_label.image = photo
        icon_label.pack(pady=10)

        # Температура
        temp_label = tk.Label(card,
                            text=f"{temp}°C",
                            font=('Segoe UI', 14, 'bold'),
                            bg=colors["secondary"],
                            fg=colors["text"])
        temp_label.pack()

        fade_in_icon(icon_label, img)

    # Создаем контейнер для прогноза на 3 дня
    daily_container = tk.Frame(frame, bg=colors["bg"], padx=20, pady=20)
    daily_container.pack(fill=tk.X)

    # Заголовок прогноза на 3 дня
    daily_title = tk.Label(daily_container,
                          text="Прогноз на 3 дня:",
                          font=('Segoe UI', 16, 'bold'),
                          bg=colors["bg"],
                          fg=colors["text"])
    daily_title.pack(pady=(0, 20))

    # Контейнер для карточек с прогнозом на 3 дня
    daily_cards = tk.Frame(daily_container, bg=colors["bg"])
    daily_cards.pack(fill=tk.X)

    for i in range(3):
        daily_cards.grid_columnconfigure(i, weight=1, uniform="equal")

    for i, (status, temp) in enumerate(daily):
        # Создаем карточку для каждого дня
        card = tk.Frame(daily_cards,
                       bg=colors["secondary"],
                       padx=20,
                       pady=20,
                       relief="flat",
                       borderwidth=1)
        card.grid(row=0, column=i, padx=10, sticky="nsew")

        # День недели
        day_label = tk.Label(card,
                           text=f"День {i+1}",
                           font=('Segoe UI', 14, 'bold'),
                           bg=colors["secondary"],
                           fg=colors["text"])
        day_label.pack(pady=(0, 10))

        # Статус погоды
        status_label = tk.Label(card,
                              text=status,
                              font=('Segoe UI', 12),
                              bg=colors["secondary"],
                              fg=colors["text"])
        status_label.pack(pady=5)

        # Температура
        temp_label = tk.Label(card,
                            text=f"{temp}°C",
                            font=('Segoe UI', 16, 'bold'),
                            bg=colors["secondary"],
                            fg=colors["text"])
        temp_label.pack() 