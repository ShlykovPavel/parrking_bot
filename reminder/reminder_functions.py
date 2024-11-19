import logging
from reminder.db_reminder_functions import db_reminder_functions
from reminder.reminder_validator import *


class reminder_functions:
    def __init__(self, bot, user_data):
        self.bot = bot
        self.user_data = user_data
        self.db = db_reminder_functions()

    def add_reminder(self, chat_id, reminder_time=None):
        logging.info(f"Добавление напоминания: chat_id={chat_id}")

        # Если время не передано, то запросим у пользователя
        if reminder_time is None:
            self.bot.send_message(chat_id, "Введите время для напоминания в формате HH:MM")
            self.bot.register_next_step_handler_by_chat_id(chat_id, self.request_reminder_time)
            return

        try:
            # Проверяем формат времени
            if not validate_time_format(reminder_time):
                self.bot.send_message(chat_id, "Некорректный формат времени. Попробуйте ещё раз (формат HH:MM)")
                self.bot.register_next_step_handler_by_chat_id(chat_id, self.request_reminder_time)
                return

            # Добавляем напоминание в базу данных
            self.db.add_reminder(chat_id, reminder_time)
            self.bot.send_message(chat_id, "Напоминание успешно добавлено")
        except Exception as e:
            logging.error(f"Ошибка добавления напоминания: {e}")
            self.bot.send_message(chat_id, "Ошибка добавления напоминания: " + str(e))

    # Новая функция для обработки повторного ввода времени
    def request_reminder_time(self, message):
        chat_id = message.chat.id
        reminder_time = message.text
        # Попробуем добавить напоминание с введённым временем
        self.add_reminder(chat_id, reminder_time)

    def delete_reminder(self, chat_id):
        logging.info(f"Удаление напоминания: chat_id={chat_id}")
        try:
            self.db.delete_reminder(chat_id)
            return self.bot.send_message(chat_id, "Напоминание успешно удалено")
        except Exception as e:
            logging.error(f"Ошибка удаления напоминания: {e}")
            return self.bot.send_message(chat_id, "Ошибка удаления напоминания: " + str(e))

    def add_parking_record(self, chat_id):
        try:
            self.db.add_parking_record(chat_id)
            return self.bot.send_message(chat_id, "Запись успешно добавлена")
        except Exception as e:
            logging.error(f"Ошибка добавления записи: {e}")
            return self.bot.send_message(chat_id, "Ошибка добавления записи: " + str(e))