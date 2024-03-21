import datetime

from flask import Flask, render_template, request, redirect
from data.users import User
from data.news import News
from data import db_session
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from forms.login import LoginForm
from forms.reg_form import RegForm
from forms.news_form import NewsForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'me_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


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
        print('Вы передали не все обязательные параметры!!!')


def add_news(author, title, text, private):
    db_sess = db_session.create_session()
    news = News()
    news.author = author
    news.title = title
    news.text = text
    news.private = private


def main():
    db_session.global_init("db/mars_explorer.db")
    app.run()


@app.route('/')
def first():
    db_sess = db_session.create_session()
    news = db_sess.query(News).all()

    authors = []
    for new in news:
        authors.append(db_sess.query(User).filter(User.id == new.author).first().name)
    info = {
        'news': news,
        'authors': authors
    }
    return render_template('news.html', **info, title='SBK')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        check_user = db_sess.query(User)
        if check_user.filter(User.email == form.email.data).first():
            return render_template('registration.html', message="Пользователь с такой почтой уже существует", form=form,
                                   title='Регистрация')

        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            age=form.age.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        user_info = db_sess.query(User).filter(User.email == form.email.data).first()
        login_user(user_info, remember=form.remember_me.data)
        return redirect('/')
    return render_template('registration.html', form=form, title='Регистрация')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if not user:
            return render_template('login.html',
                                   message="Неправильный логин",
                                   form=form, title='Вход')
        elif not user.check_password(form.password.data):
            user.set_password(form.password.data)
            return render_template('login.html',
                                   message="Неправильный пароль",
                                   form=form, title='Вход')
        login_user(user, remember=form.remember_me.data)
        return redirect("/")

    return render_template('login.html', title='Авторизация', form=form)


@app.route('/new_news', methods=['GET', 'POST'])
def new_news():
    form = NewsForm()
    print(form.data)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user_id = db_sess.query(User).filter(User.email == current_user.email).first().id
        news = News(
            author=user_id,
            name=form.name.data,
            text=form.text.data,
            private=form.private.data
        )
        db_sess.add(news)
        db_sess.commit()
        return redirect("/")
    return render_template('new_news.html', form=form, tite='Новая новость')


@app.route('/home/<name>', methods=['GET', 'POST'])
def home(name):
    if current_user.name == name:
        return render_template('home.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    main()
