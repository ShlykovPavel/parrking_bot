import logging
from datetime import datetime

from database import Database


class db_reminder_functions(Database):
    def __init__(self):
        super().__init__()
        self.db_cursor = self.cursor

    def add_reminder(self, chat_id, reminder_time):
        try:
            text = "Ты сегодня ставил машину на парковку?"
            self.db_cursor.execute('INSERT INTO reminders (chat_id, message, reminder_time) VALUES (?,?,?)', (chat_id, text, reminder_time))
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

    def add_parking_record(self, chat_id):
        try:
            username = self.db_cursor.execute('SELECT username FROM users WHERE chat_id = ?', (chat_id,)).fetchone()
            vehicle_model = self.db_cursor.execute('SELECT vehicle_model FROM users WHERE chat_id = ?', (chat_id,)).fetchone()
            vehicle_number = self.db_cursor.execute('SELECT vehicle_number FROM users WHERE chat_id = ?', (chat_id,)).fetchone()
            parking_date = datetime.now().strftime('%Y-%m-%d')
            self.db_cursor.execute('INSERT INTO parking_records (chat_id, username, parking_date, vehicle_model, vehicle_number) VALUES (?,?,?,?,?)', (chat_id, username, parking_date, vehicle_model, vehicle_number))
        except Exception as e:
            logging.error(f"Ошибка добавления записи о парковке в БД: {e}")
            return False