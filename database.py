import sqlite3

class Database:
    def __init__(self):
        # Подключение к базе данных
        self.conn = sqlite3.connect('reminders.db', check_same_thread=False)
        # Курсор взаимодействия с БД
        self.cursor = self.conn.cursor()

    def create_table(self):
        # Создание таблицы, если она не существует
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            reminder_time TEXT NOT NULL,
            reminder_message TEXT NOT NULL
        )
        ''')
        self.conn.commit()

    # Метод для закрытия соединения
    def close_connection(self):
        self.conn.close()
