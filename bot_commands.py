import logging

from telebot import types
from reminder.reminder_functions import reminder_functions
from database import Database
from users.users_functions import users_functions

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логов (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат логов
    handlers=[logging.StreamHandler()]  # Поток вывода (можно указать файл)
)


class Bot_commands:
    def __init__(self, bot, user_data):
        self.bot = bot
        self.db = Database()
        self.user_data = user_data
        self.users_functions = users_functions(self.bot, user_data)
        self.reminder_functions = reminder_functions(self.bot, user_data)

    def register_handlers(self):
        # Обработчик команды /start
        @self.bot.message_handler(commands=['start'])
        def start(message):
            chat_id = message.chat.id
            check = self.users_functions.check_users(chat_id)
            if check == True:
                self.bot.send_message(chat_id, "Вы уже зарегистрированы")
            else:
                self.user_data[chat_id] = {}
                self.bot.send_message(chat_id, "Введите своё ФИО")
                self.bot.register_next_step_handler(message, self.users_functions.get_name)

        @self.bot.message_handler(commands=['change_user'])
        def change_user(message):
            chat_id = message.chat.id
            check = self.users_functions.check_users(chat_id)
            if check == True:
                markup = types.InlineKeyboardMarkup()
                name = types.InlineKeyboardButton(text="Имя", callback_data="name")
                model = types.InlineKeyboardButton(text="Марка", callback_data="model")
                number = types.InlineKeyboardButton(text="Номер", callback_data="number")
                markup.add(name, model, number)
                self.bot.send_message(chat_id, "Выберите какой элемент вы хотите изменить", reply_markup=markup)
            else:
                self.bot.send_message(chat_id, "Вы ещё не зарегистрированы. Пожалуйста, используйте команду /start")

        @self.bot.callback_query_handler(func=lambda call: call.data in ["name", "model", "number"])
        def callback_change_user(call):
            chat_id = call.message.chat.id
            if call.data == "name":
                self.bot.send_message(chat_id, "Введите новое ФИО")
                self.bot.register_next_step_handler(call.message,
                                                    lambda msg: self.users_functions.get_name(msg, is_update=True))
            elif call.data == "model":
                self.bot.send_message(chat_id, "Введите свою марку автомобиля")
                self.bot.register_next_step_handler(call.message,
                                                    lambda msg: self.users_functions.get_vehicle_model(msg, is_update=True))
            elif call.data == "number":
                self.bot.send_message(chat_id, "Введите свой номер автомобиля")
                self.bot.register_next_step_handler(call.message, lambda msg: self.users_functions.get_vehicle_number(msg, is_update=True))

        @self.bot.message_handler(commands=['delete_user'])
        def delete_user(message):
            chat_id = message.chat.id
            try:
                users = self.users_functions.get_all_users()
                if users is not False:
                    # Создаем Inline клавиатуру
                    markup = types.InlineKeyboardMarkup()

                    # Для каждого отдела создаем кнопку
                    for user in users:
                        user_name = user[0]  # Получаем ФИО пользователя
                        markup.add(
                            types.InlineKeyboardButton(user_name, callback_data=f'username_{user_name}'))

                    # Отправляем сообщение с выбором департамента
                    self.bot.send_message(chat_id, 'Выберите пользователя которого хотите удалить', reply_markup=markup)
                else:
                    self.bot.send_message(chat_id, "Вы ещё не зарегистрированы. Пожалуйста, используйте команду /start")
            except Exception as e:
                logging.error(f"Ошибка при удалении пользователя: {e}")
                self.bot.send_message(chat_id, "Произошла ошибка при удалении пользователя")

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('username_'))
        def delete_user_from_db(callback_query):
            logging.info("username_ получен")
            chat_id = callback_query.message.chat.id
            user_name = callback_query.data.split('_')[1]
            try:
                self.users_functions.delete_user(user_name)
                self.bot.send_message(chat_id, "Пользователь успешно удалён")
            except Exception as e:
                logging.error(f"Ошибка при удалении пользователя: {e}")
                self.bot.send_message(chat_id, "Произошла ошибка при удалении пользователя")

        @self.bot.message_handler(commands=['add_reminder'])
        def add_reminder(message):
            chat_id = message.chat.id
            try:
                # Вызов функции добавления напоминания сразу после команды
                self.reminder_functions.add_reminder(chat_id)
            except Exception as e:
                logging.error(f"Ошибка добавления напоминания: {e}")
                self.bot.send_message(chat_id, "Ошибка добавления напоминания: " + str(e))

        @self.bot.message_handler(commands=['delete_reminder'])
        def delete_reminder(message):
            chat_id = message.chat.id
            try:
                # Вызов функции добавления напоминания сразу после команды
                self.reminder_functions.delete_reminder(chat_id)
            except Exception as e:
                logging.error(f"Ошибка добавления напоминания: {e}")
                self.bot.send_message(chat_id, "Ошибка добавления напоминания: " + str(e))