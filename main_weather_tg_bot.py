import requests
import datetime
from config import tg_bot_token, open_weather_token
from aiogram import Bot, types
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.utils import executor
import matplotlib.pyplot as plt

bot = Bot(token=tg_bot_token)
dp = Dispatcher(bot)

async def get_weather_info(city):
    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={open_weather_token}&units=metric"
        )
        data = r.json()

        city_name = data["name"]
        temperature = data["main"]["temp"]
        weather_description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind_speed = data["wind"]["speed"]
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = sunset_timestamp - sunrise_timestamp

        return (f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
                f"Погода в городі: {city_name}\nТемпература: {temperature}C° {weather_description}\n"
                f"Вологість: {humidity}%\nДавлення: {pressure} мм.рт.ст\nВітер: {wind_speed} м/с\n"
                f"Вихід сонця: {sunrise_timestamp}\nЗахід сонця: {sunset_timestamp}\n"
                f"Продовжність дня: {length_of_the_day}\n***Хорошого дня!***")

    except Exception as ex:
        print(ex)
        return None

async def get_temperature_graph(city):
    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={open_weather_token}&units=metric"
        )
        data = r.json()

        temperatures = []
        dates = []

        for forecast in data['list']:
            timestamp = forecast['dt']
            date = datetime.datetime.fromtimestamp(timestamp)
            day = date.strftime('%d.%m')

            if day not in dates:
                dates.append(day)
                temperatures.append([])

            index = dates.index(day)
            temperature = forecast['main']['temp']
            temperatures[index].append(temperature)

        average_temperatures = [sum(temp) / len(temp) for temp in temperatures]

        plt.figure(figsize=(8, 5))
        plt.plot(dates, average_temperatures, marker='o')
        plt.title('Середня температура за день')
        plt.xlabel('День')
        plt.ylabel('Температура, °C')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('temperature_graph.png')

        return open('temperature_graph.png', 'rb')

    except Exception as ex:
        print(ex)
        return None

async def send_weather_info(message: types.Message, city):
    weather_text = await get_weather_info(city)
    temperature_graph = await get_temperature_graph(city)

    if weather_text and temperature_graph:
        await bot.send_message(message.chat.id, weather_text)
        await bot.send_photo(message.chat.id, temperature_graph)

    else:
        await message.reply("Перевірте назву міста")

@dp.message_handler(commands=["start", "help", "prog"])
async def start_command(message: types.Message):
    if message.text == '/start':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton('/help')
        keyboard.add(button)
        await message.reply("Привіт! Натисніть /help, щоб отримати інструкції, як користуватись цим ботом.", reply_markup=keyboard)
    elif message.text == '/help':
        await message.reply("Напишіть назву міста, і я надішлю вам прогноз погоди. Наприклад Київ\n доступні команди\n /start - початок,\n /help - інструкція, \n /prog - коментар розробника")
    elif message.text == '/prog':
        await message.reply("Дякую, що ви в мене вірите:D")
        gif_path = '4MY.gif'
        with open(gif_path, 'rb') as gif:
            await bot.send_animation(message.chat.id, gif)

@dp.message_handler()
async def get_weather(message: types.Message):
    city = message.text
    await send_weather_info(message, city)

if __name__ == '__main__':
    executor.start_polling(dp)
