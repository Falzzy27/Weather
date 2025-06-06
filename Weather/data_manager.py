import json
import os
from constants import FAVORITE_CITIES_FILE, SETTINGS_FILE

def load_favorite_cities():
    if os.path.exists(FAVORITE_CITIES_FILE):
        with open(FAVORITE_CITIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_favorite_cities(cities):
    with open(FAVORITE_CITIES_FILE, "w", encoding="utf-8") as f:
        json.dump(cities, f, ensure_ascii=False, indent=2)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        try:
            interval = int(data.get("auto_update_interval", 30))
        except (ValueError, TypeError):
            interval = 30
        return {
            "auto_update_enabled": data.get("auto_update", True),
            "theme": data.get("theme", "light"),
            "auto_update_interval": interval * 60 * 1000
        }
    return {
        "auto_update_enabled": True,
        "theme": "light",
        "auto_update_interval": 30 * 60 * 1000
    }

def save_settings_to_file(auto_update, interval_minutes, theme):
    data = {
        "auto_update": auto_update,
        "theme": theme,
        "auto_update_interval": interval_minutes
    }
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Ошибка", f"Не удалось сохранить настройки:\n{e}") 