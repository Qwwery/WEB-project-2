import datetime

from flask import Flask
from data.users import User
from data.jobs import Jobs
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'me_secret_key'


def create_user(surname, name, age, position, speciality, address, email, hashed_password,
                modified_date=None):
    db_sess = db_session.create_session()
    user = User()
    user.surname = surname
    user.name = name
    user.age = age
    user.position = position
    user.speciality = speciality
    user.address = address
    user.email = email
    user.hashed_password = hashed_password
    if modified_date:
        user.modified_date = modified_date
    try:
        db_sess.add(user)
        db_sess.commit()
        print('ok')
    except Exception:
        raise Exception('Вы передали не все параметры!!!')


def add_job(team_leader, job, work_size, collaborators, start_date=None, end_date=None, is_finished=None):
    db_sess = db_session.create_session()
    jobs = Jobs()

    jobs.team_leader = team_leader
    jobs.job = job
    jobs.work_size = work_size
    jobs.collaborators = collaborators
    if start_date:
        jobs.start_date = start_date
    if end_date:
        jobs.end_date = end_date
    if is_finished:
        jobs.is_finished = is_finished
    try:
        db_sess.add(jobs)
        db_sess.commit()
    except Exception:
        raise Exception('Вы передали не все обязательные параметры!!!')


def main():
    db_session.global_init("db/mars_explorer.db")
    create_user('Scott', 'Ridley', 21, 'captain', 'research engineer', 'module_1', 'scott_chief@mars.org', '1111')
    create_user('Сахаров', 'Илья', 15, 'admin=)', 'крутой', 'module_3000', 'qwe@qwe.qwe', '1112')
    create_user('Ларионов', 'Валера', 17, 'zam.admin=)', 'крутой', 'module_3001', 'qw1e@qwe1.qwe1', '1113')
    create_user('Мотовилов', 'Григорий', 16, 'zam.zam.admin=)', 'почти крутой', 'нет', 'qwe99@qwe99.qwe99', '9999')

    add_job(1, 'deployment of residential modules 1 and 2', 15, '2, 3')
    app.run()


if __name__ == '__main__':
    main()
