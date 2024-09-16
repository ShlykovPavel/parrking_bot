import time
from datetime import datetime

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

def run_scheduler(self):
        while True:
            schedule.run_pending()
            time.sleep(1)