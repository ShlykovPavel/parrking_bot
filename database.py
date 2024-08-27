import sqlite3

# Подключение к базе данных (если файла базы данных не существует, он будет создан)
conn = sqlite3.connect('Parking.db')

# Создание курсора для выполнения SQL-запросов
cursor = conn.cursor()

# Создание таблицы
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        remind_time TEXT,
        remind_text TEXT
    )
''')

# # Вставка данных
# cursor.execute('''
#     INSERT INTO users (name, age) VALUES (?, ?)
# ''', ('Alice', 30))
#
# # Получение данных
# cursor.execute('SELECT * FROM users')
# users = cursor.fetchall()
#
# print(users)  # [(1, 'Alice', 30)]
#
# # Сохранение (commit) изменений
# conn.commit()

# Закрытие соединения
conn.close()
