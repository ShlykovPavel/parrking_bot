import logging
import time
from datetime import datetime
from functools import partial
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

        try:
            bot.send_message(chat_id, reminder_message, reply_markup=keyboard)
            logging.info(f"Напоминание отправлено пользователю {chat_id}")
        except ApiTelegramException as e:
            if "bot was blocked by the user" in str(e):
                logging.warning(f"Напоминание не отправлено. Пользователь {chat_id} заблокировал бота.")
            else:
                logging.error(f"Ошибка при отправке сообщения пользователю {chat_id}: {e}")


def run_scheduler(bot, db_cursor):
    schedule.every(1).minutes.do(partial(check_reminders, bot, db_cursor))

    while True:
        schedule.run_pending()
        time.sleep(30)