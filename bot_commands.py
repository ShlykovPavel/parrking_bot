from telebot import types


class Bot_commands:
    def __init__(self, bot, db, db_cursor):
        self.bot = bot
        self.db = db
        self.db_cursor = db_cursor

    def register_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            chat_id = message.chat.id
            # Проверка на наличие напоминания
            check = self.check_reminders_in_db(chat_id)
            if check == True:
                markup_for_edit = types.InlineKeyboardMarkup()
                button_yes = types.InlineKeyboardButton('Да', callback_data='edit_remind_yes')
                button_no = types.InlineKeyboardButton('Нет', callback_data='edit_remind_no')
                markup_for_edit.add(button_yes, button_no)
                self.bot.send_message(chat_id, 'У вас уже есть напоминание! Хотите его изменить?', reply_markup=markup_for_edit)
            else:
                markup = types.InlineKeyboardMarkup()
                button_1 = types.InlineKeyboardButton('9:00', callback_data='add_remind_9')
                button_2 = types.InlineKeyboardButton('10:00', callback_data='add_remind_10')
                button_3 = types.InlineKeyboardButton('11:00', callback_data='add_remind_11')
                markup.add(button_1, button_2, button_3)
                self.bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}. Выбери время для напоминания.', reply_markup=markup)

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('add_remind'))
        def add_remind(callback):
            chat_id = callback.message.chat.id

            if callback.data == 'add_remind_9':
                reminder_time = '9:00'
            elif callback.data == 'add_remind_10':
                reminder_time = '10:00'
            elif callback.data == 'add_remind_11':
                reminder_time = '11:00'
            else:
                return

            reminder_message = 'Напиши Оле про парковку!'
            self.add_remind_to_db(chat_id, reminder_time, reminder_message)
            self.bot.send_message(chat_id, 'Напоминание добавлено в базу данных!')

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('edit_remind'))
        def edit_remind_message(callback):
            chat_id = callback.message.chat.id
            if callback.data == 'edit_remind_yes':
                markup = types.InlineKeyboardMarkup()
                button_1 = types.InlineKeyboardButton('9:00', callback_data='edit_time_9')
                button_2 = types.InlineKeyboardButton('10:00', callback_data='edit_time_10')
                button_3 = types.InlineKeyboardButton('11:00', callback_data='edit_time_11')
                markup.add(button_1, button_2, button_3)
                self.bot.send_message(chat_id, 'Выбери время для напоминания:', reply_markup=markup)
            elif callback.data == 'edit_remind_no':
                self.bot.send_message(chat_id, 'Напоминание не было изменено.')

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('edit_time'))
        def edit_remind_time(callback):
            chat_id = callback.message.chat.id
            if callback.data == 'edit_time_9':
                reminder_time = '9:00'
            elif callback.data == 'edit_time_10':
                reminder_time = '10:00'
            elif callback.data == 'edit_time_11':
                reminder_time = '11:00'
            else:
                return
            reminder_message = 'Напиши Оле про парковку!'
            self.edit_remind_in_db(chat_id, reminder_time, reminder_message)
            self.bot.send_message(chat_id, 'Напоминание изменено в базе данных!')

    def add_remind_to_db(self, chat_id, reminder_time, reminder_message):
        self.db_cursor.execute('''
            INSERT INTO reminders (chat_id, reminder_time, reminder_message)
            VALUES (?, ?, ?)
        ''', (chat_id, reminder_time, reminder_message))
        self.db.conn.commit()

    def edit_remind_in_db(self, chat_id, reminder_time, reminder_message):
        self.db_cursor.execute('''UPDATE reminders SET reminder_time = ?, reminder_message = ? WHERE chat_id = ?''', (reminder_time, reminder_message, chat_id))
        self.db.conn.commit()

    def check_reminders_in_db(self, chat_id):
        check_by_chat_id = self.db_cursor.execute('''SELECT * FROM reminders WHERE chat_id = ?''', (chat_id,))
        if check_by_chat_id.fetchone() is not None:
            return True
        else:
            return False

    def delete_remind_from_db(self, chat_id):
        self.db_cursor.execute('''DELETE FROM reminders WHERE chat_id = ?''', (chat_id,))
        self.db.conn.commit()

    def update_remind_in_db(self, chat_id, reminder_time, reminder_message):
        self.db_cursor.execute('''UPDATE reminders SET reminder_time = ?, reminder_message = ? WHERE chat_id = ?''',
                               (reminder_time, reminder_message, chat_id))
        self.db.conn.commit()
