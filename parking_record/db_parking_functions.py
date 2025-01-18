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
            date_already_exists = self.check_parkingDate_already_exists(chat_id, date)

            if date_already_exists:
                raise ValueError("Запись о парковке уже существует")

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
            raise Exception("Ошибка добавления записи о парковке: " + str(e))

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

    def check_parkingDate_already_exists(self, chat_id, date):
        try:
            result = self.db_cursor.execute(
                '''SELECT date_parking FROM parking_records WHERE chat_id = ? AND date_parking = ?''',
                (chat_id, date)
            ).fetchall()

            # Если результат не пустой, значит запись уже существует
            return len(result) > 0
        except Exception as e:
            logging.info(f"Ошибка проверки наличия записи о парковке в БД: {e}")
            raise Exception("Ошибка проверки наличия записи о парковке: " + str(e))

    import datetime

    def get_user_parking_records(self, chat_id, month):
        try:
            # Получаем текущий год
            current_year = datetime.now().year
            # Форматируем месяц, например, 1 -> '01'
            month_str = f"{month:02d}"

            # SQL запрос, который фильтрует по году (текущий год)
            query = '''
                SELECT date_parking 
                FROM parking_records 
                WHERE chat_id = ? AND 
                      date_parking LIKE ?
            '''
            # Формируем запрос, чтобы искать записи, содержащие текущий год
            result = self.db_cursor.execute(query, (chat_id, f"%{current_year}%")).fetchall()

            # Фильтруем результат по месяцу в Python
            filtered_result = [record for record in result if record[0][3:5] == month_str]

            if filtered_result:
                logging.info(f'Результат sql запроса записей парковки пользователя {chat_id}: {filtered_result}')
                return filtered_result
            else:
                logging.info(f'Записей о парковке за месяц {month_str} для пользователя {chat_id} не найдено.')
                return None  # В случае отсутствия данных, возвращаем None
        except Exception as e:
            logging.error(f"Ошибка получения записей о парковке: {e}")
            raise Exception("Ошибка получения записей о парковке: " + str(e))
