class db_reminder_functions:
    def __init__(self, db, db_cursor):
        self.db = db
        self.db_cursor = db_cursor

        # Метод для добавления напоминания в базу данных

    def add_remind_to_db(self, chat_id, reminder_time, reminder_message):
        self.db_cursor.execute('''INSERT INTO reminders (chat_id, reminder_time, reminder_message) 
                                      VALUES (?, ?, ?)''', (chat_id, reminder_time, reminder_message))
        self.db.conn.commit()

    def get_reminder_from_db(self, chat_id):
        # Метод для получения текущего напоминания
        self.db_cursor.execute('SELECT reminder_time, reminder_message FROM reminders WHERE chat_id = ?', (chat_id,))
        return self.db_cursor.fetchone()

    def delete_remind_from_db(self, chat_id):
        # Метод для удаления напоминания из базы данных
        self.db_cursor.execute('DELETE FROM reminders WHERE chat_id = ?', (chat_id,))
        self.db.conn.commit()

    def edit_remind_in_db(self, chat_id, reminder_time, reminder_message):
        # Метод для изменения напоминания
        self.db_cursor.execute('UPDATE reminders SET reminder_time = ?, reminder_message = ? WHERE chat_id = ?',
                               (reminder_time, reminder_message, chat_id))
        self.db.conn.commit()

    def check_reminders_in_db(self, chat_id):
        check_by_chat_id = self.db_cursor.execute('''SELECT * FROM reminders WHERE chat_id = ?''', (chat_id,))
        if check_by_chat_id.fetchone() is not None:
            return True
        else:
            return False

    def update_remind_in_db(self, chat_id, reminder_time, reminder_message):
        self.db_cursor.execute('''UPDATE reminders SET reminder_time = ?, reminder_message = ? WHERE chat_id = ?''',
                               (reminder_time, reminder_message, chat_id))
        self.db.conn.commit()