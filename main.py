import schedule
import telebot
from telebot import types
import sqlite3
from datetime import datetime
import time
import threading

from bot_commands import Bot_commands
from database import Database
from remind_schedule import check_reminders, run_scheduler

# Инициализация бота
bot_api = '6878869046:AAHk5Tq4VdBAf1qc-YjfJ04-qpCBQtjo2xk'
bot = telebot.TeleBot(bot_api)



user_data = {}
bot_comands = Bot_commands(bot, user_data)
bot_comands.register_handlers()
# reminder_worker = check_reminders(bot, db_cursor)


# Планировщик задачи для проверки напоминаний каждую минуту
# schedule.every().minute.do(reminder_worker)


# Запуск бота в отдельном потоке
def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    # scheduler_thread = threading.Thread(target=run_scheduler, args=(bot))
    bot_thread = threading.Thread(target=run_bot)

    # scheduler_thread.start()
    bot_thread.start()

    # scheduler_thread.join()
    # bot_thread.join()
    print("Бот запущен")