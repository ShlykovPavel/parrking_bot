import telebot
import threading
import sqlite3
from bot_commands import Bot_commands
from reminder.remind_schedule import run_scheduler  # Импортируйте функцию планировщика

# Инициализация бота
bot_api = '7748589014:AAHjsa6H2Ur7X9rOohjywJEsg1YqDRXOUyE'
bot = telebot.TeleBot(bot_api)

# Создание подключения к базе данных
conn = sqlite3.connect('parking.db', check_same_thread=False)
db_cursor = conn.cursor()

user_data = {}
bot_commands = Bot_commands(bot, user_data)
bot_commands.register_handlers()

# Функция для запуска бота
def run_bot():
    print("Запуск бота...")
    bot.infinity_polling()

if __name__ == '__main__':
    # Создание потоков для бота и планировщика
    bot_thread = threading.Thread(target=run_bot)
    scheduler_thread = threading.Thread(target=run_scheduler, args=(bot, db_cursor))

    # Запуск потоков
    bot_thread.start()
    scheduler_thread.start()

    # Печать сообщения о запуске
    print("Бот и планировщик запущены")

    # Удалили join(), чтобы не блокировать основной поток
