import logging
from datetime import datetime

from database import Database


class db_parking_functions(Database):
    def __init__(self):
        super().__init__()
        self.db_cursor = self.cursor

    def add_parking_record(self, chat_id, date=None):
        try:
            user_data = self.get_data_for_parking_record(chat_id)
            if not user_data:
                raise ValueError("Не удалось найти данные пользователя в БД")

            username, vehicle_model, vehicle_number = user_data

            if date is not None:
                parking_date = date
            else:
                parking_date = datetime.now().strftime('%d.%m.%Y')

            self.db_cursor.execute(
                'INSERT INTO parking_records (chat_id, username, date_parking, vehicle_model, vehicle_number) VALUES (?, ?, ?, ?, ?)',
                (chat_id, username, parking_date, vehicle_model, vehicle_number))
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"Ошибка добавления записи о парковке в БД: {e}")
            return False

    def get_data_for_parking_record(self, chat_id):
        try:
            username = self.db_cursor.execute('SELECT username FROM users WHERE chat_id = ?', (chat_id,)).fetchone()
            vehicle_model = self.db_cursor.execute('SELECT vehicle_model FROM users WHERE chat_id = ?',
                                                   (chat_id,)).fetchone()
            vehicle_number = self.db_cursor.execute('SELECT vehicle_number FROM users WHERE chat_id = ?',
                                                    (chat_id,)).fetchone()

            if not (username and vehicle_model and vehicle_number):
                logging.error("Ошибка: не удалось найти данные пользователя в БД")
                return False

            # Извлекаем значения из кортежей
            username = username[0]
            vehicle_model = vehicle_model[0]
            vehicle_number = vehicle_number[0]
        except Exception as e:
            logging.error(f"Ошибка извлечения данных пользователя: {e}")
            return False

        return username, vehicle_model, vehicle_number