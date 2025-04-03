import logging
import sys
import time

import requests
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

error_event = threading.Event()
# Функция для запуска бота
def run_bot(bot):
    print("Запуск бота...")
    while True:
        try:
            bot.polling(non_stop=True)
        except requests.exceptions.ReadTimeout:
            logging.error("Произошла ошибка в основном потоке бота: ReadTimeout. Перезапуск через 60 секунд")
            time.sleep(60)

        except Exception as e:
            logging.error(f"1Произошла ошибка в основном потоке бота: {e}\n Аварийное завершение бота")
            error_event.set()
            # print(f'error_event.set() отработал')
            return


if __name__ == '__main__':
    # Создание потоков для бота и планировщика
    try:
        bot_thread = threading.Thread(target=run_bot, args=(bot,), daemon=True)
        scheduler_thread = threading.Thread(target=run_scheduler, args=(bot, db_cursor), daemon=True)

        # Запуск потоков
        bot_thread.start()
        scheduler_thread.start()

        # Печать сообщения о запуске
        print("Бот и планировщик запущены")

        while True:
            if not bot_thread.is_alive() or scheduler_thread.is_alive():
                if error_event.is_set():
                    logging.error("Обнаружена ошибка в одном из потоков. Аварийное завершение")
                    # raise Exception
                    # sys.exit(1)
                time.sleep(0.1)  # Проверяем каждую секунду

            if error_event.is_set():
                logging.error("Один из потоков завершился с ошибкой. Аварийное завершение программы")
                # sys.exit(1)
                raise Exception


    except Exception as e:
        logging.error(f"2Произошла ошибка в основном потоке: {e}\n Аварийное завершение бота")
        sys.exit(1)
