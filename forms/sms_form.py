from flask_wtf import FlaskForm
from wtforms import StringField


class SmsForm(FlaskForm):
    text = StringField("Новое сообщение")
