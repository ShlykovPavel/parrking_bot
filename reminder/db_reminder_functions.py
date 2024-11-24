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

    def delete_reminder(self, chat_id):
        try:
            self.db_cursor.execute('DELETE FROM reminders WHERE chat_id = ?', (chat_id,))
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"Ошибка удаления напоминания из БД: {e}")
            return False

    def check_reminder_time(self, chat_id, time):
        try:
            result = self.db_cursor.execute('SELECT * FROM reminders WHERE reminder_time = ? AND chat_id = ?', (time, chat_id)).fetchall()
            return len(result) > 0
        except Exception as e:
            logging.error(f"Такое время напоминания уже есть : {e}")
            raise Exception("Ошибка проверки времени напоминания: " + str(e))