from datetime import datetime


def validate_time_format(time_string):
    try:
        # Пробуем распарсить введённую строку в формат времени 'HH:MM'
        time = datetime.strptime(time_string, "%H:%M")

        # Проверяем, что минуты кратны 30
        if time.minute % 30 == 0:
            return True
        else:
            return False
    except ValueError:
        # Если строку не удалось распарсить, значит она некорректна
        return False