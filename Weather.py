from tkinter import *
from pyowm import OWM
from pyowm.utils.config import get_default_config
from pyowm.commons.exceptions import NotFoundError
root = Tk()


def click():
    city_main = message.get()


    def weather_main():
        config_dict = get_default_config()
        config_dict['language'] = 'ru'
        place = city_main
        country = ""
        country_and_place = place + ", " + country

        owm = OWM('e37dd87be727b087448120aa2552d100')
        mgr = owm.weather_manager()
        try:
            observation = mgr.weather_at_place(country_and_place)

            w = observation.weather

            status = w.detailed_status
            w.wind()
            humidity = w.humidity
            temp = w.temperature('celsius')['temp']

            def weather():
                if place == '':
                    Label(text='Город не найден!', bg='#393E46', fg='red').place(x=50, y=78)
                else:
                    def clear_frame():
                        for widgets in root.winfo_children():
                            widgets.destroy()

                    clear_frame()


                    def yep():
                        if place == '':
                            Label(text='Город не найден!', bg='393E46', fg='red').place(x=50, y=78)

                        else:
                            Label(text=("В городе " + str(place) + " сейчас " + str(status) + "\nТемпература " + str(
                                round(temp)) + " градусов по Цельсию" + "\nВлажность составляет " + str(
                                humidity) + "% " + "\nСкорость ветра " + str(w.wind()['speed']) + " метров в секунду"), bg='#393E46', fg='#00ADB5', padx='10').place(
                                x=10, y=60)

                    yep()
            weather()

        except NotFoundError:
            Label(text='Такого города не существует', bg='#393E46', fg='red').place(x=25, y=78)


    weather_main()
    city_main = message.get()


root.geometry("400x160+450+100")
root.title("Погода")
root.configure(bg='#393E46')
root.resizable(width=0, height=0)

Label(root, text='Введите ваш город:', font='0.5', bg='#393E46', fg='#EEEEEE').place(x=75, y=30)
message = StringVar()
Entry(root, textvariable=message, width=20, bg='#00ADB5').place(x=85, y=55)
Button(text='Готово', command=click, font='5', padx='25', pady='5', bg='#00ADB5').place(x=90, y=100, bordermode=OUTSIDE)

root.mainloop()