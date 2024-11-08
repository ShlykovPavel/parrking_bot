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
        logging.info(f"Добавление пользователя: chat_id={chat_id}, username={username}, vehicle_model={vehicle_model}, vehicle_number={vehicle_number}")
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

    def delete_user(self, chat_id):
        try:
            self.db.delete_user(chat_id=chat_id)
            return "Пользователь успешно удален."
        except Exception as e:
            return "Ошибка удаления пользователя: " + str(e)

    def get_name(self, message):
        chat_id = message.chat.id
        logging.info(f"Получение имени: chat_id={chat_id}, username={message.text}")
        try:
            self.user_data[chat_id]['username'] = message.text
            self.bot.send_message(chat_id, "Введите свою марку автомобиля")
            return self.bot.register_next_step_handler(message, self.get_vehicle_model)
        except Exception as e:
            return "Ошибка записи имени: " + str(e)


    def get_vehicle_model(self, message):
        chat_id = message.chat.id
        logging.info(f"Получение модели: chat_id={chat_id}, vehicle_model={message.text}")
        try:
            self.user_data[chat_id]['vehicle_model'] = message.text
            self.bot.send_message(chat_id, "Введите свой номер автомобиля")
            return self.bot.register_next_step_handler(message, self.get_vehicle_number)
        except Exception as e:
            return "Ошибка записи модели автомобиля: " + str(e)


    def get_vehicle_number(self, message):
        chat_id = message.chat.id
        logging.info(f"Получение номера: chat_id={chat_id}, vehicle_number={message.text}")
        try:
            self.user_data[chat_id]['vehicle_number'] = message.text
            logging.info("Запись в БД")
            self.add_user(chat_id=chat_id, username=self.user_data[chat_id]['username'],
                             vehicle_model=self.user_data[chat_id]['vehicle_model'],
                             vehicle_number=self.user_data[chat_id]['vehicle_number'])
            return self.bot.send_message(chat_id, "Пользователь успешно добавлен.")
        except Exception as e:
            return "Ошибка записи номера автомобиля: " + str(e)




