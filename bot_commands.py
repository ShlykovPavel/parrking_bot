import logging

from telebot import types

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логов (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат логов
    handlers=[logging.StreamHandler()]  # Поток вывода (можно указать файл)
)

class Bot_commands:
    def __init__(self, bot, db, db_cursor):
        self.bot = bot
        self.db = db
        self.db_cursor = db_cursor

    def register_handlers(self):
        # Обработчик команды /start
        @self.bot.message_handler(commands=['start'])
        def start(message):
            chat_id = message.chat.id

            # Создаем выпадающее меню
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            current_reminder_button = types.KeyboardButton('Текущее напоминание')
            add_reminder_button = types.KeyboardButton('Добавить напоминание')
            markup.add(current_reminder_button, add_reminder_button)

            self.bot.send_message(chat_id, "Привет! Используй меню для управления напоминаниями.", reply_markup=markup)

        # Обработчик нажатия кнопки "Текущее напоминание"
        @self.bot.message_handler(func=lambda message: message.text == 'Текущее напоминание')
        def show_reminder(message):
            chat_id = message.chat.id
            reminder = self.get_reminder_from_db(chat_id)

            if reminder:
                reminder_time, reminder_message = reminder
                markup = types.InlineKeyboardMarkup()
                edit_button = types.InlineKeyboardButton('Изменить напоминание', callback_data='edit_reminder')
                delete_button = types.InlineKeyboardButton('Удалить напоминание', callback_data='delete_reminder')
                markup.add(edit_button, delete_button)

                self.bot.send_message(chat_id, f'Ваше текущее напоминание на {reminder_time}: {reminder_message}',
                                      reply_markup=markup)
            else:
                self.bot.send_message(chat_id, 'У вас нет активного напоминания.')

        # Обработчик нажатия кнопки "Добавить напоминание"
        @self.bot.message_handler(func=lambda message: message.text == 'Добавить напоминание')
        def add_reminder_prompt(message):
            chat_id = message.chat.id
            reminder = self.get_reminder_from_db(chat_id)

            if reminder:
                # Если есть напоминание, предложим изменить его
                markup_for_edit = types.InlineKeyboardMarkup()
                button_yes = types.InlineKeyboardButton('Да', callback_data='edit_reminder')
                button_no = types.InlineKeyboardButton('Нет', callback_data='keep_reminder')
                markup_for_edit.add(button_yes, button_no)
                self.bot.send_message(chat_id, 'У вас уже есть напоминание! Хотите его изменить?',
                                      reply_markup=markup_for_edit)
            else:
                # Если напоминания нет, предложим добавить новое
                markup = types.InlineKeyboardMarkup()
                button_1 = types.InlineKeyboardButton('9:00', callback_data='add_remind_9')
                button_2 = types.InlineKeyboardButton('10:00', callback_data='add_remind_10')
                button_3 = types.InlineKeyboardButton('11:00', callback_data='add_remind_11')
                markup.add(button_1, button_2, button_3)
                self.bot.send_message(chat_id, 'Выберите время для нового напоминания:', reply_markup=markup)

        # Обработчик callback'ов для добавления напоминания
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('add_remind'))
        def add_reminder(callback):
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

        # Обработчик callback'ов для изменения и удаления напоминания
        @self.bot.callback_query_handler(func=lambda call: call.data == 'edit_reminder')
        def edit_reminder(callback):
            chat_id = callback.message.chat.id
            markup = types.InlineKeyboardMarkup()
            button_1 = types.InlineKeyboardButton('9:00', callback_data='edit_time_9')
            button_2 = types.InlineKeyboardButton('10:00', callback_data='edit_time_10')
            button_3 = types.InlineKeyboardButton('11:00', callback_data='edit_time_11')
            markup.add(button_1, button_2, button_3)
            self.bot.send_message(chat_id, 'Выберите новое время для напоминания:', reply_markup=markup)

        @self.bot.callback_query_handler(func=lambda call: call.data == 'delete_reminder')
        def delete_reminder(callback):
            chat_id = callback.message.chat.id
            self.delete_remind_from_db(chat_id)
            self.bot.send_message(chat_id, 'Ваше напоминание было удалено.')

        # Обработчик изменения времени напоминания
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('edit_time'))
        def edit_reminder_time(callback):
            chat_id = callback.message.chat.id
            reminder_time = callback.data.split('_')[2] + ':00'
            reminder_message = 'Напиши Оле про парковку!'
            self.edit_remind_in_db(chat_id, reminder_time, reminder_message)
            self.bot.send_message(chat_id, f'Напоминание изменено на {reminder_time}.')

