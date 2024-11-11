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
            return True
        except sqlite3.IntegrityError:
            return "Пользователь с таким chat_id уже существует."
        except Exception as e:
            logging.error(f"Ошибка добавления пользователя в БД: {e}")
            return False

    def update_user(self, chat_id, username=None, vehicle_model=None, vehicle_number=None):
        updates = []
        params = []
        try:

            if username is not None:
                updates.append("username = ?")
                params.append(username)
            if vehicle_model is not None:
                updates.append("vehicle_model = ?")
                params.append(vehicle_model)
            if vehicle_number is not None:
                updates.append("vehicle_number = ?")
                params.append(vehicle_number)

            params.append(chat_id)

            if updates:
                sql_query = f"UPDATE users SET {', '.join(updates)} WHERE chat_id = ?"
                self.cursor.execute(sql_query, tuple(params))
                self.conn.commit()
                return True
        except Exception as e:
                logging.error(f"Ошибка обновления пользователя в БД: {e}")
                return False

    def delete_user(self, username):
        try:
            self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            if self.cursor.fetchone() is not None:
                self.cursor.execute('DELETE FROM users WHERE username = ?', (username,))
                self.conn.commit()
                return True
        except Exception as e:
            logging.error(f"Ошибка удаления пользователя из БД: {e}")
            return False

    def get_all_users(self):
        try:
            self.cursor.execute('SELECT username FROM users')
            return self.cursor.fetchall()
        except Exception as e:
            logging.error(f"Ошибка получения пользователей из БД: {e}")
            return False