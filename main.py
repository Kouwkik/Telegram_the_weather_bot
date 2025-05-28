import os
import time
import re
from collections import defaultdict
from dotenv import load_dotenv
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio
from pathlib import Path # для создания папок
 # функции безопасности

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Токен бота
API_KEY = os.getenv("API_KEY") # Ключ API погоды

import logging  # импорт библиотеки для логирования

Path("logs").mkdir(exist_ok=True) # создал папку, если ее нет
logging.basicConfig(
    filename="logs/bot.log",  # Куда пишем логи
    level=logging.INFO,       # Уровень важности (INFO, WARNING, ERROR)
    format="%(asctime)s - %(message)s"  # Формат записи
)


# Инициализация бота и диспетчера
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

def is_valid(city: str) -> bool:  # функция проверки запроса
    return bool(re.match(r"^[a-zA-Zа-яА-Я\s\-]+$", city))

user_requests = defaultdict(list)

def is_rate_limited(user_id: int, limit=5, interval=30):
    now = time.time()
    user_requests[user_id] = [t for t in user_requests[user_id] if now - t < interval]
    if len(user_requests[user_id]) >= limit:
        return True
    user_requests[user_id].append(now)
    return False


# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    logging.info(f"User {message.from_user.id} started the bot")
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
    logging.info(f"User {message.from_user.id} requested weather for {message.text}")
    if not is_valid(message.text):
        await message.answer("Название города содержит недопустимые символы")
        return
    if is_rate_limited(message.from_user.id):
        await message.answer("Слишком много запросов. Подождите 1 минуту.")
        return
    try:
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&lang=ru&units=metric&appid={API_KEY}")
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
            f"<b>Погода в городе {city}</b>\n\n"
            f"• Температура: {temp}°C (ощущается как {feels_like}°C)\n"
            f"• Влажность: {humidity}%\n"
            f"• Ветер: {wind_speed} м/с\n"
            f"• Описание: {description.capitalize()}"
        )
        await message.answer(weather_report)


    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка запроса: {e}")
        await message.answer("Произошла ошибка при запросе погоды")
    except KeyError:
        logging.error(f"Некорректный ответ API для города: {message.text}")
        await message.answer("Проверьте название города")
    except Exception as e:
        logging.error(f"Неожиданная ошибка: {e}")
        await message.answer("Произошла непредвиденная ошибка")


# Функция запуска бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())