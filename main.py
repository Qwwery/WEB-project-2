from flask import Flask, render_template, request, redirect
from sqlalchemy.orm import Session

from data.users import User
from data.news import News
from data import db_session
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from forms.login import LoginForm
from forms.reg_form import RegForm
from forms.news_form import NewsForm
from forms.sms_form import SmsForm
from translate import eng_to_rus, rus_to_eng, make_translate
from data.friends import Friends

import git
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sdasdgaWFEKjwEKHFNLk;jnFKLJNpj`1`p142QEW:jqwegpoqjergplqwejg;lqeb'

login_manager = LoginManager()
login_manager.init_app(app) #test


@app.route('/secret_update', methods=["POST"])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('')
        origin = repo.remotes.origin
        origin.pull()
        return 'Ok', 200
    else:
        return 'No', 400


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init("db/db.db")
    app.run(debug=True)


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
    return render_template('news.html', **info, title='NS')


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


@app.route('/sms', methods=['GET', 'POST'])
def sms():
    form = SmsForm()
    if request.method == 'GET':
        return render_template(template_name_or_list='sms.html', form=form, title='sms')
    else:
        if 'btn_submit' in request.form:  # не релизнуто, пока что просто стирает
            form.text.data = ""
            print('btn_submit was pressed')
        elif 'btn_translate_eng' in request.form:
            form.text.data = make_translate(form.text.data, rus_to_eng)
            print('btn_translate_eng was pressed')
        elif 'btn_translate_russ' in request.form:
            form.text.data = make_translate(form.text.data, eng_to_rus)
            print('btn_translate_russ was pressed')
        return render_template(template_name_or_list='sms.html', form=form, title='sms')


@app.route('/search_user')
def search_user():
    db_sess = db_session.create_session()
    all_users = db_sess.query(User).filter(User.id != current_user.id).all()

    not_friends = []
    for elem in all_users:
        check_users = db_sess.query(Friends).filter(Friends.first_id == current_user.id, Friends.second_id == elem.id).first()
        if not check_users or check_users.mans_attitude != 'friends':
            not_friends.append(elem)

    info = {
        'users': not_friends
    }

    return render_template('search_user.html', **info, title='Поиск друзей')


@app.route('/user/<int:id>', methods=['GET', 'POST'])
def user(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()

    info = {
        'user': user
    }

    if request.method == 'POST':
        if 'add_friend' in request.form:
            data_friend = [current_user.id, id]
            print(data_friend)

            check_blocked = db_sess.query(Friends).filter(Friends.first_id == id, Friends.second_id == current_user.id).first()
            if check_blocked and check_blocked.mans_attitude == 'ban': # перед оправкой дружбы проверяем, не заблокирован ли отправитель
                return render_template('user_id.html', **info, title=user.name, text='Пользователь вас заблокировал')

            check_friend = db_sess.query(Friends).filter(Friends.first_id == current_user.id, Friends.second_id == id).first()
            if not check_friend:  # если это первый запрос на дружбу и нет блокировок
                first_zapic = Friends()
                first_zapic.first_id = current_user.id
                first_zapic.second_id = id
                first_zapic.mans_attitude = 'sent'

                second_zapic = Friends()
                second_zapic.first_id = id
                second_zapic.second_id = current_user.id
                second_zapic.mans_attitude = 'received'

                db_sess.add(second_zapic)

                db_sess.add(first_zapic)

                db_sess.commit()
                return render_template('user_id.html', **info, title=user.name, text='Запрос был отправлен', button_info='add')

            else:
                if check_friend.mans_attitude == 'ban':  # пользователь заблокирован текущим пользователем, отправить никак
                    return render_template('user_id.html', **info, title=user.name, text='Вы не можете отправить запрос этому пользователю.', button_info='add')

                elif check_friend.mans_attitude == 'sent':  # запрос на ожидании
                    return render_template('user_id.html', **info, title=user.name, text='Вы уже отправляли запрос этому пользователю', button_info='add')
                elif check_friend.mans_attitude == 'received':
                    return render_template('user_id.html', **info, title=user.name, text='Этот пользователь хочет с вами дружить!', button_info='add')
        elif 'sumbit' in request.form:
            check_friend = db_sess.query(Friends).filter(Friends.first_id == current_user.id,
                                                         Friends.second_id == id).first()
            check_friend.mans_attitude = 'friends'

            check_friend_2 = db_sess.query(Friends).filter(Friends.first_id == id,
                                                         Friends.second_id == current_user.id).first()
            check_friend_2.mans_attitude = 'friends'

            db_sess.commit()

            return redirect('/')
    try:
        check_friend = db_sess.query(Friends).filter(Friends.first_id == current_user.id, Friends.second_id == id).first()
        if check_friend.mans_attitude == 'received':
                return render_template('user_id.html', **info, title=user.name, text='Этот пользователь хочет с вами дружить!', button_info='sumbit')
    except Exception: # записи не нашлось в бд
        return render_template('user_id.html', **info, title=user.name, text='', button_info='add')

    check_friend = db_sess.query(Friends).filter(Friends.first_id == current_user.id, Friends.second_id == id).first()
    if check_friend.mans_attitude == 'friends':
        return render_template('user_id.html', **info, title=user.name, text='', button_info='other')
    return render_template('user_id.html', **info, title=user.name, text='', button_info='add')

@app.route('/friends')
def friends():
    db_sess = db_session.create_session()
    friends_info = db_sess.query(Friends).filter(Friends.second_id == current_user.id, Friends.mans_attitude == 'friends').all()
    friends_id = list(map(lambda x: x.first_id, friends_info))
    friends = db_sess.query(User).filter(User.id.in_(friends_id)).all()
    return render_template('friends.html', friends=friends)


@app.route('/friend_requests')
def friend_requests():
    db_sess = db_session.create_session()
    friend_requests = db_sess.query(Friends).filter(Friends.first_id == current_user.id, Friends.mans_attitude == 'received').all()
    if not current_user:
        return redirect('/')

    users = []
    for user in friend_requests:
        user = db_sess.query(User).filter(User.id == user.second_id).first()
        users.append(user)
    info = {
        'users': users,
        'title': 'Заявки в друзья'
    }
    return render_template('friend_requests.html', **info)


if __name__ == '__main__':
    main()
