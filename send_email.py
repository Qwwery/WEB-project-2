# valerysite06@gmail.com - почта
from string import ascii_letters, digits
from random import sample
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def generage_code():
    simvols = list(ascii_letters + digits)
    code = ''.join(sample(simvols, k=15))
    return code


def send_email(code_check):
    # Заполните эти поля вашими данными
    sender_email = "valerysite06@gmail.com"
    receiver_email = "manahova@yandexlyceum.ru"  # кому
    password = "cwat iden voof bxdn"
    subject = "Subject of the email"
    body = code_check

    # Создание объекта сообщения
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    # Добавление тела письма
    message.attach(MIMEText(body, 'plain'))

    # Создание объекта сессии SMTP
    session = smtplib.SMTP('smtp.gmail.com', 587)  # Укажите здесь свой SMTP сервер
    session.starttls()  # Активация шифрования
    session.login(sender_email, password)  # Авторизация на сервере

    # Отправка сообщения
    session.sendmail(sender_email, receiver_email, message.as_string())
    session.quit()

    print("Email sent successfully.")


code = generage_code()
