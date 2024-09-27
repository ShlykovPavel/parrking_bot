import time
from datetime import datetime
from functools import partial
import schedule

def check_reminders(bot, db_cursor):
    current_time = datetime.now().strftime('%H:%M')
    db_cursor.execute('''
        SELECT chat_id, reminder_message FROM reminders WHERE reminder_time = ?
    ''', (current_time,))
    reminders = db_cursor.fetchall()

    for reminder in reminders:
        chat_id, reminder_message = reminder
        bot.send_message(chat_id, reminder_message)

def run_scheduler(bot, db_cursor):
    # Используем partial для передачи аргументов в check_reminders
    schedule.every().day.at("09:00").do(partial(check_reminders, bot, db_cursor))
    schedule.every().day.at("10:00").do(partial(check_reminders, bot, db_cursor))
    schedule.every().day.at("11:00").do(partial(check_reminders, bot, db_cursor))


    while True:
        schedule.run_pending()
        time.sleep(1)
