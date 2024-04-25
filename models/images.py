import sqlalchemy
from .db_session import SqlAlchemyBase


class Images(SqlAlchemyBase):
    __tablename__ = 'images'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    b64_image = sqlalchemy.Column(sqlalchemy.String)
