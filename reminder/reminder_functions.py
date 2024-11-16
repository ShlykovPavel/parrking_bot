import logging
from reminder.db_reminder_functions import db_reminder_functions


class reminder_functions:
    def __init__(self, bot, user_data):
        self.bot = bot
        self.user_data = user_data
        self.db = db_reminder_functions()

    def add_reminder(self, chat_id):
        logging.info(f"Добавление напоминания: chat_id={chat_id}")
        try:
            self.db.add_reminder(chat_id)
            return self.bot.send_message(chat_id, "Напоминание успешно добавлено")
        except Exception as e:
            logging.error(f"Ошибка добавления напоминания: {e}")
            return self.bot.send_message(chat_id, "Ошибка добавления напоминания: " + str(e))

    def delete_reminder(self, chat_id):
        logging.info(f"Удаление напоминания: chat_id={chat_id}")
        try:
            self.db.delete_reminder(chat_id)
            return self.bot.send_message(chat_id, "Напоминание успешно удалено")
        except Exception as e:
            logging.error(f"Ошибка удаления напоминания: {e}")
            return self.bot.send_message(chat_id, "Ошибка удаления напоминания: " + str(e))