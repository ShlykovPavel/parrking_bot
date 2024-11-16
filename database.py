import sqlite3

class Database:
    def __init__(self):
        # Подключение к базе данных
        self.conn = sqlite3.connect('parking.db', check_same_thread=False)
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
