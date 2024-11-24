import logging
from datetime import datetime

from database import Database


class db_reminder_functions(Database):
    def __init__(self):
        super().__init__()
        self.db_cursor = self.cursor

    def add_reminder(self, chat_id, reminder_time):
        try:
            exist_time = self.check_reminder_time(chat_id, reminder_time)
            if exist_time:
                raise ValueError("Запись о парковке уже существует")

            text = "Ты сегодня ставил машину на парковку?"
            self.db_cursor.execute('INSERT INTO reminders (chat_id, message, reminder_time) VALUES (?,?,?)', (chat_id, text, reminder_time))
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"Ошибка добавления напоминания в БД: {e}")
            raise Exception(f"{e}")

    def delete_reminder(self, chat_id, time):
        try:
            self.db_cursor.execute('DELETE FROM reminders WHERE chat_id = ? AND reminder_time = ?', (chat_id, time))
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"Ошибка удаления напоминания из БД: {e}")
            raise Exception(f"{e}")

    def check_reminder_time(self, chat_id, time):
        try:
            result = self.db_cursor.execute('SELECT * FROM reminders WHERE reminder_time = ? AND chat_id = ?', (time, chat_id)).fetchall()
            return len(result) > 0
        except Exception as e:
            logging.error(f"Такое время напоминания уже есть : {e}")
            raise Exception("Ошибка проверки времени напоминания: " + str(e))

    def get_all_user_reminders(self, chat_id):
        try:
            result = self.db_cursor.execute('SELECT reminder_time FROM reminders WHERE chat_id = ?', (chat_id,)).fetchall()
            return result
        except Exception as e:
            logging.error(f"Ошибка получения напоминаний: {e}")
            raise Exception("Ошибка получения напоминаний: " + str(e))