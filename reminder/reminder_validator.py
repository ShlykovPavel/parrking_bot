import logging
from datetime import datetime


class ValidationError(Exception):
    """Пользовательское исключение для ошибок валидации."""
    pass


class Validator:
    def __init__(self, bot):
        self.bot = bot

    def validate_time_format(self, time_string):
        try:
            # Пробуем распарсить введённую строку в формат времени 'HH:MM'
            time = datetime.strptime(time_string, "%H:%M")

            # Проверяем, что минуты кратны 30
            if time.minute % 30 != 0:
                raise ValidationError("Некорректный формат времени. Минуты должны быть кратны 30.")

            # Если формат корректен, возвращаем True
            return True
        except ValueError:
            # Если строку не удалось распарсить, выбрасываем исключение
            raise ValidationError("Некорректный формат времени. Используйте формат ЧЧ:ММ.")


    def validate_date_format(self, date_string):
        try:
            # Пробуем распарсить введённую строку в формат даты 'DD.MM.YYYY'
            date = datetime.strptime(date_string, "%d.%m.%Y")
            today = datetime.today()

            # Проверяем, что введённая дата не позже сегодняшнего дня
            if date > today:
                raise ValidationError("Дата не может быть позже сегодняшнего дня.")

            return True
        except ValueError:
            # Если строку не удалось распарсить, значит она некорректна
            raise ValidationError("Некорректный формат даты. Используйте формат ДД.ММ.ГГГГ.")