import datetime

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String)
    surname = sqlalchemy.Column(sqlalchemy.String)
    age = sqlalchemy.Column(sqlalchemy.Integer)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    city = sqlalchemy.Column(sqlalchemy.String, default='Не указан')
    news_relationship = orm.relationship("News", back_populates="user_relationship")
    confirmed = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    setup = sqlalchemy.Column(sqlalchemy.String)
    setup_see = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    domen = sqlalchemy.Column(sqlalchemy.String)

    def __repr__(self):
        return f"<User> id:{self.id}, surname:{self.surname}, name:{self.name}"

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
