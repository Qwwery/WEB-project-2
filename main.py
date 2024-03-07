import datetime

from flask import Flask
from data.users import User
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'me_secret_key'

def crezte_user(surname, name, age, position, speciality, address, email, hashed_password, modified_date=datetime.datetime.now()):
    db_sess = db_session.create_session()
    user = User()
    try:
        user.surname = surname
        user.name = name
        user.age = age
        user.position = position
        user.speciality = speciality
        user.address = address
        user.email = email
        user.hashed_password = hashed_password
        user.modified_date = modified_date
    except Exception:
        raise Exception('Вы передали не все параметры!!!')
    db_sess.add(user)
    db_sess.commit()
    print('ok')

def main():
    db_session.global_init("db/mars_explorer.db")
    crezte_user('Scott', 'Ridley', 21, 'captain', 'research engineer', 'module_1', 'scott_chief@mars.org', '1111')
    crezte_user('Сахаров', 'Илья', 15, 'admin=)', 'крутой', 'module_3000', 'qwe@qwe.qwe', '1112')
    crezte_user('Ларионов', 'Валера', 17, 'zam.admin=)', 'крутой', 'module_3001', 'qw1e@qwe1.qwe1', '1113')
    crezte_user('Мотовилов', 'Григорий', 16, 'zam.zam.admin=)', 'почти крутой', 'нет', 'qwe99@qwe99.qwe99', '9999')
    app.run()


if __name__ == '__main__':
    main()
