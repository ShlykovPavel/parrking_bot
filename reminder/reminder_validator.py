from datetime import datetime


class Validator:
    def __init__(self, bot):
        self.bot = bot

    def validate_time_format(self, time_string):
        try:
            # Пробуем распарсить введённую строку в формат времени 'HH:MM'
            time = datetime.strptime(time_string, "%H:%M")

            # Проверяем, что минуты кратны 30
            if time.minute % 30 == 0:
                return True, "Время корректно."
            else:
                return False, "Некорректный формат времени."
        except ValueError:
            # Если строку не удалось распарсить, значит она некорректна
            return False, "Некорректный формат времени."

    def request_new_time(self, chat_id, callback_func):
        # Запрашиваем новое время у пользователя
        self.bot.send_message(chat_id, "Введите корректные данные")

        # Используем register_next_step_handler, чтобы обработать следующий ввод
        self.bot.register_next_step_handler_by_chat_id(chat_id, lambda message: self.validate_and_callback(message,
                                                                                                           callback_func))

    def validate_and_callback(self, message, callback_func):
        chat_id = message.chat.id
        new_time = message.text

        # Проверяем формат времени
        is_valid, error_message = self.validate_time_format(new_time)

        if is_valid:
            # Если время корректно, вызываем переданную функцию-обработчик с новым временем
            callback_func(chat_id, new_time)
        else:
            # Если время некорректно, используем сообщение об ошибке
            self.bot.send_message(chat_id, error_message)
            self.request_new_time(chat_id, callback_func)

    def validate_date_format(self, date_string):
        try:
            # Пробуем распарсить введённую строку в формат даты 'DD.MM.YYYY'
            date = datetime.strptime(date_string, "%d.%m.%Y")
            today = datetime.today()

            # Проверяем, что введённая дата не позже сегодняшнего дня
            if date > today:
                return False, "Дата не может быть в будущем."

            return True, "Дата корректна."
        except ValueError:
            # Если строку не удалось распарсить, значит она некорректна
            return False, "Некорректный формат даты. Используйте формат ДД.ММ.ГГГГ."
