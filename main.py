from flask import Flask, render_template, request, redirect, abort
from sqlalchemy.orm import Session

import ast
from time import time
import requests
from data.users import User  # test 2
from data.news import News
from data import db_session
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from forms.login import LoginForm
from forms.reg_form import RegForm
from forms.news_form import NewsForm
from forms.sms_form import SmsForm
from forms.edit_news_form import EditNewsForm
from translate import eng_to_rus, rus_to_eng, make_translate
from data.friends import Friends
from data.messages import Messages
from time_news import get_str_time  # deleted
import datetime
import git
import json
import pytz
import logging
from itsdangerous import URLSafeTimedSerializer
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sdasdgaWFEKjwEKHFNLk;jnFKLJNpj`1`p142QEW:jqwegpoqjergplqwejg;lqeb'
db_session.global_init("db/db.db")


def main():
    db_session.global_init("db/db.db")
    app.run(debug=True)


serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


database = []


@app.route('/send', methods=['POST'])
def send():
    data = request.json
    print(data)

    name = data['name']
    text = data['text']

    if not isinstance(data, dict) or 'name' not in data or 'text' not in data:
        return abort(404)

    message = {
        'name': name,
        'text': text,
        'time': time()
    }

    database.append(message)

    return {'ok': True}


@app.route(f'/messages', methods=['GET', 'POST'])
def get_message():
    db_sess = db_session.create_session()
    data = request.args

    try:
        author = data['author']
        before = data['before']
        assert int(current_user.id) == int(author)
        friends = db_sess.query(Friends).filter(Friends.first_id == author, Friends.second_id == before).first()
        assert friends

    except Exception:
        return abort(404)

    messages = db_sess.query(Messages).filter(((Messages.author == author) & (Messages.before == before)) | (
            (Messages.author == before) & (Messages.before == author))).all()

    if messages is None:
        if friends.mans_attitude == 'friends':
            messages = Messages(author=author, before=before, js_message='{}')
            db_sess.add(messages)
            db_sess.commit()
        else:
            abort(404)

    form = SmsForm()
    if request.method == 'POST' and form.validate_on_submit():
        name = current_user.name
        text = request.form['text']
        if 'btn_submit' in request.form:
            response = requests.post(url="http://127.0.0.1:5000/send", json={"name": name, "text": text})

            if text.strip():
                new_message = Messages(author=author, before=before, js_message=str({"name": name, "text": text}))
                db_sess.add(new_message)
                db_sess.commit()
            return redirect(f'/messages?author={author}&before={before}')

        elif 'btn_translate_eng' in request.form:
            form.text.data = make_translate(form.text.data, rus_to_eng)
            result_message = []
            for message in messages:
                result_message.append(ast.literal_eval(message.js_message))
            print(result_message)
            info = {
                'messages': result_message
            }
            return render_template('sms.html', **info, form=form)
        elif 'btn_translate_russ' in request.form:
            form.text.data = make_translate(form.text.data, eng_to_rus)
            result_message = []
            for message in messages:
                result_message.append(ast.literal_eval(message.js_message))
            info = {
                'messages': result_message
            }
            return render_template('sms.html', **info, form=form)

        else:
            name = current_user.name
            text = request.form['text']
            response = requests.post(url="http://127.0.0.1:5000/send", json={"name": name, "text": text})

            new_message = Messages(author=author, before=before, js_message=str({"name": name, "text": text}))
            db_sess.add(new_message)
            db_sess.commit()
            return redirect(f'/messages?author={author}&before={before}')

    elif request.method == 'GET':
        result_message = []
        for message in messages:
            result_message.append(ast.literal_eval(message.js_message))
        print(result_message)
        info = {
            'messages': result_message
        }
        return render_template('sms.html', **info, form=form)


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

    # return db_sess.query(User).get(user_id)
    return db_sess.get(User, user_id)


@app.route('/', methods=['GET', 'POST'])
def first():
    db_sess = db_session.create_session()
    text = ''
    if request.method == 'POST':
        if 'confirm' in request.form:
            user = db_sess.query(User).filter(User.email == current_user.email).first()
            confirmation_code = serializer.dumps(user.id, salt='confirm-salt')
            confirm_url = f'{request.host}/confirm/{confirmation_code}'
            msg = MIMEText(f'''Подтвердите учетную запись от NaSvyazi, перейдя по ссылке: {confirm_url}.\n 
            Если вы не отправляли запрос, игнорируйте это сообщение''', 'html')
            msg['Subject'] = 'Account Confirmation Required'
            msg['From'] = 'valerylarionov06@gmail.com'
            msg['To'] = user.email

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login('valerylarionov06@gmail.com', 'hafg vjqg nywe khnu')
                server.sendmail('valerylarionov06@gmail.com', [user.email], msg.as_string())
                text = 'Зайдите на почту и подтвердите свою учетную запись в течение трёх минут'

    news = db_sess.query(News).all()
    news = news[::-1]

    authors = []
    for new in news:
        name = db_sess.query(User).filter(User.id == new.author).first().name
        surname = db_sess.query(User).filter(User.id == new.author).first().surname
        authors.append(f"{surname} {name}")
        # new.data = get_str_time(new.data)
        new.date = datetime.datetime.now()
    info = {
        'news': news,
        'authors': authors
    }

    return render_template('news.html', **info, title='NaSvyazi', text=text, action='')


@app.route('/edit_news/<int:id>', methods=['GET', 'POST'])
@login_required
def news_edit(id):
    form = EditNewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        new_check = db_sess.query(News).filter(News.id == id).filter(News.author == current_user.id).first()
        if current_user.email == 'regeneration76@yandex.ru' or current_user.email == 'valerylarionov06@gmail.com':
            new_check = db_sess.query(News).filter(News.id == id).first()

        if new_check:
            form.name.data = new_check.name
            form.text.data = new_check.text
            form.private.data = new_check.private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        new_obj = db_sess.query(News).filter(News.id == id).filter(News.author == current_user.id).first()
        if current_user.email == 'regeneration76@yandex.ru' or current_user.email == 'valerylarionov06@gmail.com':
            new_obj = db_sess.query(News).filter(News.id == id).first()
        if 'edit' in request.form:
            if new_obj:
                if len(form.name.data.strip()) > 100:
                    return render_template('edit_news.html', title='Редактирование работы', form=form, action='',
                                           message=f'Слишком длинное название: {len(form.name.data.strip())} (максимум 100 символов)')
                if len(form.text.data.strip()) > 1000:
                    return render_template('edit_news.html', title='Редактирование работы', form=form, action='',
                                           message=f'Слишком длинное описание {len(form.text.data.strip())} (максимум 1000 символов)')
                new_obj.name = form.name.data.strip()
                new_obj.text = form.text.data
                new_obj.private = form.private.data
                db_sess.merge(new_obj)
                db_sess.commit()
                return redirect('/')

        elif 'confirm_del' in request.form:
            return render_template('edit_news.html', title='Редактирование работы', form=form, action='confirm_del')
        elif 'yes' in request.form:
            if new_obj:
                db_sess.delete(new_obj)
                db_sess.commit()
            else:
                abort(404)
            return redirect('/')
    return render_template('edit_news.html', title='Редактирование работы', form=form, action='')


@app.route('/confirm/<confirmation_code>')
def confirm(confirmation_code):
    db_sess = db_session.create_session()
    try:
        unconfirmed_user_id = serializer.loads(confirmation_code, salt='confirm-salt', max_age=180)
        user = db_sess.query(User).filter(User.id == unconfirmed_user_id).first()

        if unconfirmed_user_id is not None:
            user.confirmed = True
            db_sess.commit()

            return render_template('home.html', text='Вы подтвердили вашу учетную запись')
        else:
            return render_template('confirmed_sms.html', title='NaSvyazi', text='Неизвестная ошибка')
    except Exception as text:
        print(text)
        return render_template('confirmed_sms.html', title='NaSvyazi',
                               text='Ошибка, возможно, превышено время. Попробуйте еще раз')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        check_user = db_sess.query(User)
        if check_user.filter(User.email == form.email.data).first():
            return render_template('registration.html',
                                   message="Ошибка регистрации: пользователь с такой почтой уже существует", form=form,
                                   title='Регистрация')
        age = form.age.data
        if age < 1 or age > 150:
            return render_template('registration.html', message="Ошибка регистрации: что с возрастом?", form=form,
                                   title='Регистрация')
        name = form.name.data.strip()
        if len(name) > 30:
            return render_template('registration.html', message="Ошибка регистрации: Слишком длинное имя", form=form,
                                   title='Регистрация')
        surname = form.surname.data.strip()
        if len(surname) > 30:
            return render_template('registration.html', message="Ошибка регистрации: Слишком длинная фамилия",
                                   form=form,
                                   title='Регистрация')
        if not form.city.data:
            city = 'Не указан'
        else:
            city = form.city.data.strip()
        user = User(
            name=name,
            surname=surname,
            email=form.email.data,
            age=form.age.data,
            city=city
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
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user_id = db_sess.query(User).filter(User.email == current_user.email).first().id
        if len(form.name.data.strip()) > 100:
            return render_template('new_news.html', title='Редактирование работы', form=form, action='',
                                   message=f'Слишком длинное название: {len(form.name.data.strip())} (максимум 100 символов)')
        if len(form.text.data.strip()) > 1000:
            return render_template('new_news.html', title='Редактирование работы', form=form, action='',
                                   message=f'Слишком длинное описание {len(form.text.data.strip())} (максимум 1000 символов)')
        news = News(
            author=user_id,
            name=form.name.data,
            text=form.text.data,
            private=form.private.data,
        )

        db_sess.add(news)
        db_sess.commit()
        tz_kiev = pytz.timezone('Europe/Kiev')
        time_kiev = datetime.datetime.now(tz_kiev)
        news.data = time_kiev
        news.data_str = get_str_time(news.data)
        db_sess.commit()
        return redirect("/")
    return render_template('new_news.html', form=form, title='Новая новость')


@app.route('/home/<int:id>', methods=['GET', 'POST'])
def home(id):
    try:
        id_user = current_user.id
    except Exception:
        abort(404)
    if id_user == id:
        if 'confirm' in request.form:
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == current_user.email).first()
            confirmation_code = serializer.dumps(user.id, salt='confirm-salt')
            confirm_url = f'{request.host}/confirm/{confirmation_code}'
            msg = MIMEText(f'''Please confirm your account by clicking the link below: {confirm_url}''', 'html')
            msg['Subject'] = 'Account Confirmation Required'
            msg['From'] = 'valerylarionov06@gmail.com'
            msg['To'] = user.email

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login('valerylarionov06@gmail.com', 'hafg vjqg nywe khnu')
                server.sendmail('valerylarionov06@gmail.com', [user.email], msg.as_string())
            return render_template('home.html', title=current_user.name,
                                   text='Зайдите на почту и подтвердите свою учетную запись в течение трёх минут')
        return render_template('home.html', title=current_user.name, text='')
    else:
        abort(404)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/im', methods=['GET', 'POST'])
def im():
    if not current_user.is_authenticated:
        return '<h1 align="center">Войди в аккаунт, и не балуйся с ссылками ;)</h1>'
    form = SmsForm()
    id_user = request.args.get('sel')
    id_chat = request.args.get('ch')

    db_sess = db_session.create_session()
    is_friends = db_sess.query(Friends).filter(Friends.first_id == current_user.id, Friends.second_id == id_user).all()
    if is_friends:
        user = db_sess.query(User).filter(User.id == id_user).first()
    else:
        return redirect('404')

    if user:
        return render_template(template_name_or_list='im.html', form=form, title=user.name)


@login_required
@app.route('/search_user', methods=['GET', 'POST'])
def search_user():
    db_sess = db_session.create_session()
    all_users = db_sess.query(User).filter(User.id != current_user.id).all()

    not_friends = []
    for elem in all_users:
        check_users = db_sess.query(Friends).filter(Friends.first_id == current_user.id,
                                                    Friends.second_id == elem.id).first()
        if not check_users or check_users.mans_attitude != 'friends':
            not_friends.append(elem)

    info = {
        'users': not_friends
    }

    if request.method == 'POST' and 'search' in request.form and len(request.form['search'].strip()) > 0:
        name_search = request.form['search']
        if len(name_search.strip()) > 0:
            user_with_search = []
            for elem in not_friends:
                if name_search.lower() in elem.name.lower():
                    user_with_search.append(elem)
            info = {
                'users': user_with_search
            }
        return render_template('search_user.html', **info, title='Поиск друзей', action='btn')
    elif request.method == 'POST' and 'all' in request.form:
        return render_template('search_user.html', **info, title='Поиск друзей', action='')
    return render_template('search_user.html', **info, title='Поиск друзей', action='')


@app.route('/user/<int:id>', methods=['GET', 'POST'])
def user(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()

    info = {
        'user': user
    }
    if request.method == 'POST':
        if 'add_friend' in request.form:

            check_blocked = db_sess.query(Friends).filter(Friends.first_id == id,
                                                          Friends.second_id == current_user.id).first()
            if check_blocked and check_blocked.mans_attitude == 'ban':  # перед оправкой дружбы проверяем, не заблокирован ли отправитель
                return render_template('user_id.html', **info, title=user.name, text='Пользователь вас заблокировал')

            check_friend = db_sess.query(Friends).filter(Friends.first_id == current_user.id,
                                                         Friends.second_id == id).first()
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
                return render_template('user_id.html', **info, title=user.name, text='Запрос был отправлен',
                                       button_info='sent')

            else:
                if check_friend.mans_attitude == 'ban':  # пользователь заблокирован текущим пользователем, отправить никак
                    return render_template('user_id.html', **info, title=user.name,
                                           text='Вы не можете отправить запрос этому пользователю.', button_info='add')

                elif check_friend.mans_attitude == 'sent':  # запрос на ожидании
                    return render_template('user_id.html', **info, title=user.name,
                                           text='Вы уже отправляли запрос этому пользователю', button_info='sent')
                elif check_friend.mans_attitude == 'received':
                    return render_template('user_id.html', **info, title=user.name,
                                           text='Этот пользователь хочет с вами дружить!', button_info='add')
        elif 'sumbit' in request.form:
            check_friend = db_sess.query(Friends).filter(Friends.first_id == current_user.id,
                                                         Friends.second_id == id).first()
            check_friend.mans_attitude = 'friends'
            check_friend_2 = db_sess.query(Friends).filter(Friends.first_id == id,
                                                           Friends.second_id == current_user.id).first()
            check_friend_2.mans_attitude = 'friends'
            db_sess.commit()
            return redirect('/')
        elif 'delete' in request.form:
            return render_template('user_id.html', **info, title=user.name, button_info='dialog', name=user.name)
        elif 'yes' in request.form:
            first = db_sess.query(Friends).filter(Friends.first_id == id, Friends.second_id == current_user.id).first()
            second = db_sess.query(Friends).filter(Friends.first_id == current_user.id, Friends.second_id == id).first()
            db_sess.delete(first)
            db_sess.delete(second)
            db_sess.commit()
            return render_template('user_id.html', **info, title=user.name,
                                   text=f'Пользователь {user.name} был удален из ваших друзей', button_info='add')
        elif 'cancel_friend' in request.form:
            first = db_sess.query(Friends).filter(Friends.first_id == id, Friends.second_id == current_user.id).first()
            second = db_sess.query(Friends).filter(Friends.first_id == current_user.id, Friends.second_id == id).first()
            db_sess.delete(first)
            db_sess.delete(second)
            db_sess.commit()
            return render_template('user_id.html', **info, title=user.name, text='Предложение отклонено',
                                   button_info='add')
        elif 'cancel_request' in request.form:
            first = db_sess.query(Friends).filter(Friends.first_id == id, Friends.second_id == current_user.id).first()
            second = db_sess.query(Friends).filter(Friends.first_id == current_user.id, Friends.second_id == id).first()
            db_sess.delete(first)
            db_sess.delete(second)
            db_sess.commit()
            return render_template('user_id.html', **info, title=user.name, text='Запрос отменен',
                                   button_info='add')
    try:
        check_friend = db_sess.query(Friends).filter(Friends.first_id == current_user.id,
                                                     Friends.second_id == id).first()
        if check_friend.mans_attitude == 'received':
            return render_template('user_id.html', **info, title=user.name,
                                   text='Этот пользователь хочет с вами дружить!', button_info='sumbit')
    except Exception:  # записи не нашлось в бд
        try:
            return render_template('user_id.html', **info, title=user.name, text='', button_info='add')
        except Exception:
            abort(404)

    check_friend = db_sess.query(Friends).filter(Friends.first_id == current_user.id, Friends.second_id == id).first()
    if check_friend.mans_attitude == 'friends':
        return render_template('user_id.html', **info, title=user.name, text='', button_info='other')
    if check_friend.mans_attitude == 'sent':
        return render_template('user_id.html', **info, title=user.name, text='', button_info='sent')
    return render_template('user_id.html', **info, title=user.name, text='', button_info='add')


@app.route('/friends', methods=['GET', 'POST'])
def friends():
    db_sess = db_session.create_session()
    friends_info = db_sess.query(Friends).filter(Friends.second_id == current_user.id,
                                                 Friends.mans_attitude == 'friends').all()
    friends_id = list(map(lambda x: x.first_id, friends_info))
    friends = db_sess.query(User).filter(User.id.in_(friends_id)).all()

    if request.method == 'POST' and 'search' in request.form and len(request.form['search'].strip()) > 0:
        friends = list(filter(lambda x: request.form['search'].lower() in x.name.lower(), friends))
        return render_template('friends.html', friends=friends, title='Друзья', action='btn')
    elif request.method == 'POST' and 'all' in request.form:
        return render_template('friends.html', friends=friends, title='Друзья', action='')
    return render_template('friends.html', friends=friends, title='Друзья', action='')


@app.route('/friend_requests')
def friend_requests():
    db_sess = db_session.create_session()
    friend_requests = db_sess.query(Friends).filter(Friends.first_id == current_user.id,
                                                    Friends.mans_attitude == 'received').all()
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


@app.route('/help')
def help():
    return render_template('help.html')


if __name__ == '__main__':
    main()
