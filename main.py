import os
import datetime
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio


TOKEN = "8046767990:AAG5oaNbtVnbQwG_15VpuvKBc3kx2cTyc8M"
API = '02fe506f35a3696595afdf914336c71b'

# Инициализация бота и диспетчера
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "Привет! Напиши мне название города и я пришлю сводку погоды\n\n"
        "Доступные функции:\n"
        "• Температура 🌡\n"
        "• Осадки 🌧\n"
        "• Ветер 💨"
    )

# Обработчик текстовых сообщений
@dp.message()
async def get_weather_of_city(message: types.Message):
    try:
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&lang=ru&units=metric&appid={API}")
        data = response.json()

        # Парсим сайт, извлекаем данные
        city = data['name']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        description = data['weather'][0]['description']

        # Формируем ответ
        weather_report = (
            f"<b>Погода в {city}</b>\n\n"
            f"• Температура: {temp}°C (ощущается как {feels_like}°C)\n"
            f"• Влажность: {humidity}%\n"
            f"• Ветер: {wind_speed} м/с\n"
            f"• Описание: {description.capitalize()}"
        )
        await message.answer(weather_report)

    except:
        await message.answer("Проверьте название города")


# Функция запуска бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())