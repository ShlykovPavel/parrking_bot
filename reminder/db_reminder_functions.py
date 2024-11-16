import logging
from database import Database


class db_reminder_functions(Database):
    def __init__(self):
        super().__init__()
        self.db_cursor = self.cursor

    def add_reminder(self, chat_id):
        try:
            text = "Ты сегодня ставил машину на парковку?"
            self.db_cursor.execute('INSERT INTO reminders (chat_id, message) VALUES (?,?)', (chat_id, text))
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"Ошибка добавления напоминания в БД: {e}")
            return False

    def delete_reminder(self, chat_id):
        try:
            self.db_cursor.execute('DELETE FROM reminders WHERE chat_id = ?', (chat_id,))
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"Ошибка удаления напоминания из БД: {e}")
            return False