import logging
import os
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.apihelper import ApiTelegramException
from admin_pass import Administrate
from parking_record.parking_functions import parking_functions
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
        self.parking_functions = parking_functions(self.bot, user_data)
        self.administrate = Administrate(self.bot)

    def admin_only(self, func):
        def wrapper(message, *args, **kwargs):
            chat_id = message.chat.id
            self.bot.send_message(chat_id, "Введите пароль администратора")
            # Передаем обработчик для проверки пароля
            self.bot.register_next_step_handler(
                message,
                lambda msg: self.administrate.check_password_and_execute(msg, func, *args, **kwargs)
            )

        return wrapper

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
        @self.admin_only
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
                                                    lambda msg: self.users_functions.update_name(msg))
            elif call.data == "model":
                self.bot.send_message(chat_id, "Введите свою марку автомобиля")
                self.bot.register_next_step_handler(call.message,
                                                    lambda msg: self.users_functions.update_vehicle_model(msg))
            elif call.data == "number":
                self.bot.send_message(chat_id, "Введите свой номер автомобиля")
                self.bot.register_next_step_handler(call.message,
                                                    lambda msg: self.users_functions.update_vehicle_number(msg))

        @self.bot.message_handler(commands=['delete_user'])
        @self.admin_only
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
            else:
                pass

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('username_'))
        def delete_user_from_db(callback_query):
            logging.info("username_ получен")
            chat_id = callback_query.message.chat.id
            user_name = callback_query.data.split('_')[1]
            try:
                self.users_functions.delete_user_and_reminders(user_name, chat_id)
                self.bot.send_message(chat_id, "Пользователь успешно удалён")
            except Exception as e:
                logging.error(f"Ошибка при удалении пользователя: {e}")
                self.bot.send_message(chat_id, "Произошла ошибка при удалении пользователя")

        @self.bot.message_handler(commands=['add_reminder'])
        def add_reminder(message):
            chat_id = message.chat.id
            try:
                self.bot.send_message(chat_id,
                                      "Пожалуйста, введите время в формате HH:MM с шагом в 30 минут для добавления напоминания.")
                self.bot.register_next_step_handler(message,
                                                    lambda message: self.reminder_functions.add_reminder(chat_id,
                                                                                                         message.text))
            except Exception as e:
                logging.error(f"Ошибка добавления напоминания: {e}")
                self.bot.send_message(chat_id, "Ошибка добавления напоминания: " + str(e))

        @self.bot.message_handler(commands=['delete_reminder'])
        def delete_reminder(message):
            chat_id = message.chat.id
            reminders = self.reminder_functions.get_reminders(chat_id)
            if reminders is not False:
                # Создаем Inline клавиатуру
                markup = types.InlineKeyboardMarkup()

                # Для каждого напоминания создаем кнопку
                for reminder in reminders:
                    reminder_time = reminder[0]  # Получаем время напоминания
                    markup.add(
                        types.InlineKeyboardButton(reminder_time, callback_data=f'time_{reminder_time}'))

                # Отправляем сообщение с выбором напоминания
                self.bot.send_message(chat_id, 'Выберите напоминание которое хотите удалить', reply_markup=markup)
            else:
                self.bot.send_message(chat_id,
                                      "Вы ещё не добавили напоминания. Пожалуйста, используйте команду /add_reminder")

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('time_'))
        def delete_reminder_from_db(call):
            chat_id = call.message.chat.id
            reminder_time = call.data.split('_')[1]
            try:
                self.reminder_functions.delete_reminder(chat_id, reminder_time)
            except Exception as e:
                logging.error(f"Ошибка при удалении напоминания: {e}")
                self.bot.send_message(chat_id, f"Произошла ошибка при удалении напоминания + {e}")

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('reminder_'))
        def reminder_handler(call):
            chat_id = call.message.chat.id
            try:
                # Извлекаем информацию из callback_data
                action = call.data
                chat_id = int(chat_id)

                if action == "reminder_yes":
                    self.parking_functions.reminder_add_parking_record(chat_id)

                elif action == "reminder_no":
                    self.bot.send_message(chat_id, "Вы ответили 'Нет'. Спасибо за ответ.")
                # Удалим клавиатуру после нажатия
                self.bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                   reply_markup=None)
            except Exception as e:
                logging.error(f"Ошибка обработки ответа на напоминание: {e}")

        @self.bot.message_handler(commands=['add_parking_record'])
        def add_parking_record(message):
            chat_id = message.chat.id
            try:
                self.bot.send_message(chat_id, "Пожалуйста, введите дату в формате ДД.ММ.ГГГГ")
                self.bot.register_next_step_handler(message,
                                                    lambda message: self.parking_functions.manual_add_parking_record(
                                                        chat_id, message.text))
            except Exception as e:
                logging.error(f"Ошибка добавления записи: {e}")
                self.bot.send_message(chat_id, "Ошибка добавления записи: " + str(e))

        @self.bot.message_handler(commands=['get_table'])
        @self.admin_only
        def get_table(message):
            chat_id = message.chat.id

            def ask_month(message):
                self.bot.send_message(chat_id, "Введите номер месяца в формате ММ")
                self.bot.register_next_step_handler(message, ask_year)

            def ask_year(message):
                try:
                    month = int(message.text)
                    self.bot.send_message(chat_id, "Введите год в формате ГГГГ")
                    self.bot.register_next_step_handler(message, lambda m: generate_report(m, month))
                except ValueError:
                    self.bot.send_message(chat_id, "Пожалуйста, введите правильный номер месяца.")
                    ask_month(message)

            def generate_report(message, month):
                try:
                    year = int(message.text)
                    file_path = self.db.get_xlsx_from_db(month, year)
                    with open(file_path, 'rb') as file:
                        self.bot.send_document(chat_id, file)
                    os.remove(file_path)
                except ValueError:
                    self.bot.send_message(chat_id, "Пожалуйста, введите правильный год.")
                    ask_year(message)

            ask_month(message)

        @self.bot.message_handler(commands=['user_list'])
        @self.admin_only
        def get_user_list(message):
            chat_id = message.chat.id
            try:
                users = self.users_functions.get_all_users()
                if users is not False:
                    user_list = "\n".join(f"👤 {user[0]}" for user in users)
                    self.bot.send_message(chat_id, f"📋 Список зарегистрировавшихся пользователей:\n\n{user_list}")
                else:
                    self.bot.send_message(chat_id, "Нет пользователей")
            except Exception as e:
                logging.error(f"Ошибка при получении списка пользователей: {e}")
                self.bot.send_message(chat_id, "Произошла ошибка при получении списка пользователей")

        @self.bot.message_handler(commands=['send_everyone'])
        @self.admin_only
        def send_everyone(message):
            chat_id = message.chat.id
            try:
                users = self.users_functions.get_all_users_chat_ids()
                if users is not False:
                    for user in users:
                        user_name = user[0]  # Получаем chat_id пользователя
                        # Создание Inline-клавиатуры с кнопками
                        keyboard = InlineKeyboardMarkup()
                        yes_button = InlineKeyboardButton(text="Да", callback_data=f"reminder_yes")
                        no_button = InlineKeyboardButton(text="Нет", callback_data=f"reminder_no")
                        keyboard.add(yes_button, no_button)

                        try:
                            self.bot.send_message(user_name, 'Ты сегодня ставил машину на парковку?',
                                                  reply_markup=keyboard)
                            logging.info(f"Напоминание отправлено пользователю {user_name}")
                        except ApiTelegramException as e:
                            if "bot was blocked by the user" in str(e):
                                logging.warning(
                                    f"Напоминание не отправлено. Пользователь {user_name} заблокировал бота.")
                            else:
                                logging.error(f"Ошибка при отправке сообщения пользователю {user_name}: {e}")
                else:
                    self.bot.send_message(chat_id, "Нет пользователей")
            except Exception as e:
                logging.error(f"Ошибка при отправке напоминаний: {e}")
                self.bot.send_message(chat_id, "Произошла ошибка при отправке напоминаний")

        @self.bot.message_handler(commands=['get_parking_records'])
        def get_user_parking_records(message):
            chat_id = message.chat.id

            def ask_month(message):
                self.bot.send_message(chat_id, "Введите номер месяца в формате ММ (например, 01 для января)")
                self.bot.register_next_step_handler(message, process_month)

            def process_month(message):
                try:
                    month = int(message.text)
                    if month < 1 or month > 12:
                        raise ValueError("Месяц должен быть числом от 1 до 12")

                    # Получаем записи о парковке за этот месяц
                    records = self.parking_functions.get_user_parking_records(chat_id, month)

                    if records:
                        # Если записи есть, показываем их пользователю
                        result = "\n".join(
                            [record[0] for record in records])  # Предполагаем, что записанные даты в формате строки
                        self.bot.send_message(chat_id, f"Записи о парковке за месяц {month}:\n{result}")
                    else:
                        # Если записей нет
                        self.bot.send_message(chat_id, f"Нет записей о парковке за месяц {month}.")
                except ValueError as ve:
                    # Обработка ошибки валидации (например, пользователь ввёл не число)
                    self.bot.send_message(chat_id, f"Ошибка: неправильный формат даты. Попробуйте снова.")
                    logging.error(f"Ошибка валидации введённого времени при запросе записей о парковке пользователя {chat_id}: {ve}")
                except Exception as e:
                    logging.error(f"Ошибка получения данных о парковке: {e}")
                    self.bot.send_message(chat_id,
                                          "Произошла ошибка при получении данных о парковке. Попробуйте снова.")

            # Начинаем с запроса месяца
            ask_month(message)
