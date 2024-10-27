class db_users_functions:
    def __init__(self, db):
        self.db = db
        self.db_cursor = self.db.cursor()

    def add_user(self, chat_id, username, vehicle_model, vehicle_number):
        self.db_cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
        if self.db_cursor.fetchone() is None:
            self.db_cursor.execute(
                'INSERT INTO users (chat_id, username, vehicle_model, vehicle_number) VALUES (?,?,?,?)',
                (chat_id, username, vehicle_model, vehicle_number))
            self.db.conn.commit()
            return "User added successfully."
        else:
            return "User already exists."