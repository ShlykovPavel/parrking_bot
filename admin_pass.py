import os


class Administrate():
    def __init__(self, bot):
        self.bot = bot


    def check_password_and_execute(self, message, func, *args, **kwargs):
        chat_id = message.chat.id
        if message.text == os.getenv('Admin_password'):
            self.bot.send_message(chat_id, "Доступ разрешен.")
            func(message, *args, **kwargs)  # Выполняем функцию после успешной проверки
        else:
            self.bot.send_message(chat_id, "Неправильный пароль. Попробуйте снова.")
