from telebot import types


class Bot_commands:
    def __init__(self, bot, db, db_cursor):
        self.bot = bot
        self.db = db
        self.db_cursor = db_cursor

    def register_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            markup = types.InlineKeyboardMarkup()
            button_1 = types.InlineKeyboardButton('9:00', callback_data='add_remind_9')
            button_2 = types.InlineKeyboardButton('10:00', callback_data='add_remind_10')
            button_3 = types.InlineKeyboardButton('11:00', callback_data='add_remind_11')
            markup.add(button_1, button_2, button_3)
            self.bot.send_message(message.chat.id,
                                  f'Привет, {message.from_user.first_name}. Выбери время для напоминания.',
                                  reply_markup=markup)

        @self.bot.callback_query_handler(func=lambda call: True)
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

    def add_remind_to_db(self, chat_id, reminder_time, reminder_message):
        self.db_cursor.execute('''
            INSERT INTO reminders (chat_id, reminder_time, reminder_message)
            VALUES (?, ?, ?)
        ''', (chat_id, reminder_time, reminder_message))
        self.db.conn.commit()
