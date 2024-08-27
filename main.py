import schedule
import telebot
from telebot import types
import sqlite3
from datetime import datetime
import time
import threading

# Инициализация бота
bot_api = '6878869046:AAHk5Tq4VdBAf1qc-YjfJ04-qpCBQtjo2xk'
bot = telebot.TeleBot(bot_api)

# Подключение к базе данных
conn = sqlite3.connect('reminders.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    reminder_time TEXT NOT NULL,
    reminder_message TEXT NOT NULL
)
''')
conn.commit()

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    button_1 = types.InlineKeyboardButton('9:00', callback_data='add_remind_9')
    button_2 = types.InlineKeyboardButton('10:00', callback_data='add_remind_10')
    button_3 = types.InlineKeyboardButton('11:00', callback_data='add_remind_11')
    markup.add(button_1, button_2, button_3)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}. Выбери время для напоминания.', reply_markup=markup)

# Обработчик нажатия кнопки
@bot.callback_query_handler(func=lambda call: True)
def add_remind(callback):
    chat_id = callback.message.chat.id  # Получаем chat_id

    if callback.data == 'add_remind_9':
        reminder_time = '9:00'
    elif callback.data == 'add_remind_10':
        reminder_time = '10:00'
    elif callback.data == 'add_remind_11':
        reminder_time = '11:00'
    else:
        return  # Если callback_data не совпадает ни с одной из предусмотренных

    reminder_message = 'Напиши Оле про парковку!'
    add_remind_to_db(chat_id, reminder_time, reminder_message)
    bot.send_message(chat_id, 'Напоминание добавлено в базу данных!')

# Функция добавления напоминания в базу данных
def add_remind_to_db(chat_id, reminder_time, reminder_message):
    cursor.execute('''
        INSERT INTO reminders (chat_id, reminder_time, reminder_message)
        VALUES (?, ?, ?)
    ''', (chat_id, reminder_time, reminder_message))
    conn.commit()

# Функция для извлечения напоминаний на текущее время
def check_reminders():
    current_time = datetime.now().strftime('%H:%M')
    cursor.execute('''
        SELECT chat_id, reminder_message FROM reminders WHERE reminder_time = ?
    ''', (current_time,))
    reminders = cursor.fetchall()

    for reminder in reminders:
        chat_id, reminder_message = reminder
        bot.send_message(chat_id, reminder_message)

# Планировщик задачи для проверки напоминаний каждую минуту
schedule.every().minute.do(check_reminders)

# Запуск планировщика в отдельном потоке
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Запуск бота в отдельном потоке
def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    scheduler_thread = threading.Thread(target=run_scheduler)
    bot_thread = threading.Thread(target=run_bot)

    scheduler_thread.start()
    bot_thread.start()

    scheduler_thread.join()
    bot_thread.join()