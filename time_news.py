import pymorphy2


def get_str_time(data):
    months_english_to_russian = {
        "January": "Январь",
        "February": "Февраль",
        "March": "Март",
        "April": "Апрель",
        "May": "Май",
        "June": "Июнь",
        "July": "Июль",
        "August": "Август",
        "September": "Сентябрь",
        "October": "Октябрь",
        "November": "Ноябрь",
        "December": "Декабрь"
    }

    year = data.year
    day = data.day
    month = months_english_to_russian[data.strftime("%B")]
    hour = str(data.hour).rjust(2, '0')
    minute = str(data.minute).rjust(2, '0')

    morph = pymorphy2.MorphAnalyzer()
    month = morph.parse(month)[0]
    month = month.inflect({'gent'}).word

    data = f'{day} {month} {year} в {hour}:{minute}'
    return data
