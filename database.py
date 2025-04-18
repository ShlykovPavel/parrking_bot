import os
import sqlite3
import pandas as pd
import openpyxl


def ensure_db_exists(db_path):
    # Извлекаем имя папки из пути к файлу базы данных
    folder_path = os.path.dirname(db_path)

    # Проверяем, существует ли папка; если нет, создаём её
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Папка '{folder_path}' создана.")

    # Проверяем, существует ли файл базы данных; если нет, создаём его
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.close()  # Закрываем соединение, чтобы файл базы данных был создан
        print(f"Файл базы данных '{db_path}' создан.")


class Database:
    def __init__(self):
        # Подключение к базе данных
        self.conn = sqlite3.connect('Database/parking.db', check_same_thread=False)
        # Курсор взаимодействия с БД
        self.cursor = self.conn.cursor()
        self.create_reminders_table()
        self.create_users_table()
        self.create_parking_records_table()

    def create_users_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            vehicle_model TEXT NOT NULL,
            vehicle_number TEXT NOT NULL
        )''')
        self.conn.commit()

    def create_parking_records_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            vehicle_model TEXT NOT NULL,
            vehicle_number TEXT NOT NULL,
            username TEXT NOT NULL,
            date_parking TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        )
        ''')
        self.conn.commit()

    def create_reminders_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            reminder_time TEXT NOT NULL,
            FOREIGN KEY (chat_id) REFERENCES users (chat_id)
        )''')
        self.conn.commit()
    # Метод для закрытия соединения
    def close_connection(self):
        self.conn.close()

    def get_xlsx_from_db(self, month, year):
        month_str = str(month).zfill(2)
        year = str(year)
        query = """
            SELECT * FROM parking_records
            WHERE substr(date_parking, 4, 2) = ?
            AND substr(date_parking, 7, 4) = ?
        """
        df = pd.read_sql(query, self.conn, params=(month_str, year))
        print(f"Результат sql запроса: {df}")
        file_path = 'Database/result.xlsx'
        df.to_excel(file_path, index=False)
        return file_path