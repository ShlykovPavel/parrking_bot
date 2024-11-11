import logging

from users.db_users_functions import db_users_functions

logging.basicConfig(
    level=logging.INFO,  # Уровень логов (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат логов
    handlers=[logging.StreamHandler()]  # Поток вывода (можно указать файл)
)


class users_functions:
    def __init__(self, bot, user_data):
        self.bot = bot
        self.db = db_users_functions()
        self.user_data = user_data

    def check_users(self, chat_id):
        try:
            return self.db.check_users_in_db(chat_id)
        except Exception as e:
            return "Ошибка проверки пользователя: " + str(e)

    def add_user(self, chat_id, username, vehicle_model, vehicle_number):
        logging.info(
            f"Добавление пользователя: chat_id={chat_id}, username={username}, vehicle_model={vehicle_model}, vehicle_number={vehicle_number}")
        try:
            self.db.add_user(chat_id=chat_id, username=username, vehicle_model=vehicle_model,
                             vehicle_number=vehicle_number)
            return "Пользователь успешно добавлен."
        except Exception as e:
            return "Ошибка добавления пользователя: " + str(e)

    def update_user(self, chat_id, username, vehicle_model, vehicle_number):
        try:
            self.db.update_user(chat_id=chat_id, username=username, vehicle_model=vehicle_model,
                                vehicle_number=vehicle_number)
            return "Пользователь успешно обновлен."
        except Exception as e:
            return "Ошибка обновления пользователя: " + str(e)

    def delete_user(self, username):
        try:
            self.db.delete_user(username=username)
            return True
        except Exception as e:
            return "Ошибка удаления пользователя: " + str(e)

    def get_name(self, message, is_update=False):
        chat_id = message.chat.id
        logging.info(f"Получение имени: chat_id={chat_id}, username={message.text}")
        try:
            if chat_id not in self.user_data:
                self.user_data[chat_id] = {}

            if is_update == False:
                self.user_data[chat_id]['username'] = message.text
                self.bot.send_message(chat_id, "Введите свою марку автомобиля")
                return self.bot.register_next_step_handler(message, lambda msg: self.get_vehicle_model(msg, is_update))
            else:
                self.user_data[chat_id]['username'] = message.text
                self.db.update_user(chat_id=chat_id, username=self.user_data[chat_id]['username'])
                self.bot.send_message(chat_id, "Имя успешно обновлено.")
        except Exception as e:
            logging.error(f"Ошибка записи имени: {e}")
            return self.bot.send_message(chat_id, "Ошибка записи имени")

    def get_vehicle_model(self, message, is_update=False):
        chat_id = message.chat.id
        logging.info(f"Получение модели: chat_id={chat_id}, vehicle_model={message.text}")
        try:
            if is_update == False:
                self.user_data[chat_id]['vehicle_model'] = message.text
                self.bot.send_message(chat_id, "Введите свой номер автомобиля")
                return self.bot.register_next_step_handler(message, lambda msg: self.get_vehicle_number(msg, is_update))
            else:
                self.user_data[chat_id]['vehicle_model'] = message.text
                self.db.update_user(chat_id=chat_id,
                                    vehicle_model=self.user_data[chat_id]['vehicle_model'])
                self.bot.send_message(chat_id, "Модель автомобиля успешно обновлена.")
        except Exception as e:
            logging.error(f"Ошибка записи модели автомобиля: {e}")
            return self.bot.send_message(chat_id, "Ошибка записи модели автомобиля")

    def get_vehicle_number(self, message, is_update=False):
        chat_id = message.chat.id
        logging.info(f"Получение номера: chat_id={chat_id}, vehicle_number={message.text}")
        try:
            self.user_data[chat_id]['vehicle_number'] = message.text
            if is_update == True:
                # Логика для обновления
                self.db.update_user(chat_id=chat_id,
                                    vehicle_number=self.user_data[chat_id]['vehicle_number'])
                return self.bot.send_message(chat_id, "Номер автомобиля успешно обновлён.")
            else:
                # Логика для добавления
                self.db.add_user(chat_id=chat_id, username=self.user_data[chat_id]['username'],
                                 vehicle_model=self.user_data[chat_id]['vehicle_model'],
                                 vehicle_number=self.user_data[chat_id]['vehicle_number'])
                return self.bot.send_message(chat_id, "Пользователь успешно добавлен.")
        except Exception as e:
            logging.error(f"Ошибка записи номера автомобиля: {e}")
            return self.bot.send_message(chat_id, "Ошибка записи номера автомобиля")

    def get_all_users(self):
        try:
            return self.db.get_all_users()
        except Exception as e:
            logging.error(f"Ошибка получения пользователей из БД: {e}")
            return False
