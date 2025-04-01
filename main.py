import logging
import sys
import telebot
import threading
import sqlite3
from bot_commands import Bot_commands
from reminder.remind_schedule import run_scheduler
import os
from dotenv import load_dotenv
from database import ensure_db_exists


db_path = 'Database/parking.db'
load_dotenv()
# Инициализация бота
bot_api = os.getenv('Bot_api')
bot = telebot.TeleBot(bot_api)

# Создание подключения к базе данных
ensure_db_exists(db_path)
conn = sqlite3.connect('Database/parking.db', check_same_thread=False)
db_cursor = conn.cursor()

user_data = {}
bot_commands = Bot_commands(bot, user_data)
bot_commands.register_handlers()

# Функция для запуска бота
def run_bot():
    try:
        print("Запуск бота...")
        bot.infinity_polling()
    except Exception as e:
        logging.error(f"Произошла ошибка в основном потоке бота: {e}\n Аварийное завершение бота")
        sys.exit(1)

if __name__ == '__main__':
    # Создание потоков для бота и планировщика
    try:
        bot_thread = threading.Thread(target=run_bot)
        scheduler_thread = threading.Thread(target=run_scheduler, args=(bot, db_cursor))

        # Запуск потоков
        bot_thread.start()
        scheduler_thread.start()

        # Печать сообщения о запуске
        print("Бот и планировщик запущены")
    except Exception as e:
        logging.error(f"Произошла ошибка в основном потоке: {e}\n Аварийное завершение бота")
        sys.exit(1)
