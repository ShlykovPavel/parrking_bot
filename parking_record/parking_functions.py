import logging
from parking_record.db_parking_functions import db_parking_functions
from reminder.reminder_validator import *

class parking_functions:
    def __init__(self, bot, user_data):
        self.bot = bot
        self.db = db_parking_functions()
        self.user_data = user_data
        self.time_validator = Validator(bot)

    def reminder_add_parking_record(self, chat_id):
        try:
            self.db.add_parking_record(chat_id)
            return self.bot.send_message(chat_id, "Запись успешно добавлена")
        except Exception as e:
            logging.error(f"Ошибка добавления записи: {e}")
            return self.bot.send_message(chat_id, "Ошибка добавления записи: " + str(e))

    def manual_add_parking_record(self, chat_id, date):
        try:
            is_valid, validation_message = self.time_validator.validate_date_format(date)

            if not is_valid:
                self.bot.send_message(chat_id, validation_message)
                self.bot.register_next_step_handler_by_chat_id(chat_id,
                                                               lambda message: self.manual_add_parking_record(chat_id,
                                                                                                              message.text))
                return

            self.db.add_parking_record(chat_id, date=date)
            return self.bot.send_message(chat_id, "Запись успешно добавлена")
        except Exception as e:
            logging.error(f"Ошибка добавления записи: {e}")
            return self.bot.send_message(chat_id, "Ошибка добавления записи: " + str(e))
