import aiohttp
from io import BytesIO
from PIL import Image
from constants import IP_TOKEN, WEATHER_TOKEN

async def get_city_by_ip():
    url = "http://ip-api.com/json/"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    city = data.get("city")
                    if city:
                        return city
                    else:
                        print("Город не найден в ответе.")
                else:
                    print(f"Ошибка запроса: статус {resp.status}")
    except Exception as e:
        print(f"Не удалось получить город по IP: {e}")
    return None

async def fetch_icon(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                image_bytes = await response.read()
                return Image.open(BytesIO(image_bytes))
    except Exception as e:
        print(f"Ошибка при загрузке иконки: {e}")
    return None

async def get_weather_data_async(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?APPID={WEATHER_TOKEN}&lang=ru&q={city}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    return "not_found"
                data = await response.json()

            hourly_forecast = []
            for item in data['list'][:8]:
                dt = item['dt_txt'][11:16]
                temp = round(item['main']['temp'] - 273.15)
                icon_url = f"http://openweathermap.org/img/wn/{item['weather'][0]['icon']}.png"
                icon_img = await fetch_icon(session, icon_url)
                hourly_forecast.append((dt, temp, icon_img))

            daily_data = {}
            for item in data['list']:
                date = item['dt_txt'][:10]
                temp = round(item['main']['temp'] - 273.15)
                status = item['weather'][0]['description']
                daily_data.setdefault(date, []).append((temp, status))

            daily_forecast = []
            for date, values in list(daily_data.items())[:3]:
                avg_temp = round(sum(t for t, _ in values) / len(values))
                status = values[0][1]
                daily_forecast.append((status, avg_temp))

            return hourly_forecast, daily_forecast

    except Exception as e:
        print(f"Ошибка при запросе погоды: {e}")
        return None 