import logging
import sys
import threading
import time
from datetime import datetime
from functools import partial
# from main import *
import requests
import schedule
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import holidays
from telebot.apihelper import ApiTelegramException


def check_reminders(bot, db_cursor, country_code='RU'):
    current_day = datetime.now().weekday()

    holidays_list = holidays.country_holidays(country_code)
    current_date = datetime.now().date()

    if current_day >= 5 or current_date in holidays_list:
        logging.info("Сегодня выходной или праздничный день, напоминания не будут отправлены.")
        return

    current_time = datetime.now().strftime('%H:%M')
    db_cursor.execute('''
        SELECT chat_id, message FROM reminders WHERE reminder_time = ?
    ''', (current_time,))
    reminders = db_cursor.fetchall()

    for reminder in reminders:
        chat_id, reminder_message = reminder

        # Создание Inline-клавиатуры с кнопками
        keyboard = InlineKeyboardMarkup()
        yes_button = InlineKeyboardButton(text="Да", callback_data=f"reminder_yes")
        no_button = InlineKeyboardButton(text="Нет", callback_data=f"reminder_no")
        keyboard.add(yes_button, no_button)
        i = 0
        while i < 3:
            try:
                logging.info(f"Попытка # {i + 1} отправить напоминание юзеру: {chat_id}")
                bot.send_message(chat_id, reminder_message, reply_markup=keyboard)
                logging.info(f"Напоминание отправлено пользователю {chat_id}")
                break
            except ApiTelegramException as e:
                if "bot was blocked by the user" in str(e):
                    logging.warning(f"Напоминание не отправлено. Пользователь {chat_id} заблокировал бота.")
                    break
                else:
                    logging.error(f"Ошибка при отправке сообщения пользователю {chat_id}: {e}")
                    break
            except requests.exceptions.ReadTimeout:
                logging.error(f"Произошла ошибка в потоке планировщика бота: ReadTimeout. Ожидание 10 секунд. \nПопытка: {i}")
                time.sleep(10)
                i += 1
                if i == 3:  # После трёх попыток
                    logging.error(f"Исчерпаны 3 попытки для {chat_id}. ")
                    raise Exception("Max retries exceeded for ReadTimeout")

            except Exception as e:
                logging.error(f"Ошибка при отправке сообщения пользователю {chat_id}: {e}\n Попытка: {i}")
                i += 1

error_event = threading.Event()
def run_scheduler(bot, db_cursor):
    try:
        schedule.every(1).minutes.do(partial(check_reminders, bot, db_cursor))

        while True:
            schedule.run_pending()
            time.sleep(30)
    except Exception as e:
        logging.error(f"Произошла ошибка в потоке планировщика бота: {e}\n Аварийное завершение бота")
        error_event.set()
        sys.exit(1)
