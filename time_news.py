def get_str_time(data):
    months_english_to_russian = {
        "January": "Января",
        "February": "Февраля",
        "March": "Марта",
        "April": "Апреля",
        "May": "Мая",
        "June": "Июня",
        "July": "Июля",
        "August": "Авгуса",
        "September": "Сентября",
        "October": "Октября",
        "November": "Ноября",
        "December": "Декабря"
    }
    year = data.year
    day = data.day
    month = months_english_to_russian[data.strftime("%B")]
    hour = str(data.hour).rjust(2, '0')
    minute = str(data.minute).rjust(2, '0')

    data = f'{day} {month} {year} в {hour}:{minute}'
    return data
