import logging
import sqlite3

from database import Database


class db_users_functions(Database):
    def __init__(self):
        super().__init__()
        self.db_cursor = self.cursor

    def check_users_in_db(self, chat_id):
        check_by_chat_id = self.cursor.execute('''SELECT * FROM users WHERE chat_id = ?''', (chat_id,))
        if check_by_chat_id.fetchone() is not None:
            return True
        else:
            return False

    def add_user(self, chat_id, username, vehicle_model, vehicle_number):
        try:
            self.db_cursor.execute(
                'INSERT INTO users (chat_id, username, vehicle_model, vehicle_number) VALUES (?, ?, ?, ?)',
                (chat_id, username, vehicle_model, vehicle_number)
            )
            self.conn.commit()
            return "Пользователь успешно добавлен."
        except sqlite3.IntegrityError:
            return "Пользователь с таким chat_id уже существует."
        except Exception as e:
            logging.error(f"Ошибка добавления пользователя в БД: {e}")
            return "Ошибка добавления пользователя в БД."

    def update_user(self, chat_id, username, vehicle_model, vehicle_number):
        self.cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
        if self.cursor.fetchone() is not None:
            self.cursor.execute('UPDATE users SET username = ?, vehicle_model = ?, vehicle_number = ? WHERE chat_id = ?',
                               (username, vehicle_model, vehicle_number, chat_id))
            self.conn.commit()
            return "User updated successfully."
        else:
            return "User does not exist."

    def delete_user(self, chat_id):
        self.cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
        if self.cursor.fetchone() is not None:
            self.cursor.execute('DELETE FROM users WHERE chat_id = ?', (chat_id,))
            self.conn.commit()
            return "User deleted successfully."
        else:
            return "User does not exist."