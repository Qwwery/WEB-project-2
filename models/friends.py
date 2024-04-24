import sqlalchemy
from .db_session import SqlAlchemyBase


class Friends(SqlAlchemyBase):
    __tablename__ = 'friends'

    bundle_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    first_id = sqlalchemy.Column(sqlalchemy.Integer)
    second_id = sqlalchemy.Column(sqlalchemy.Integer)
    mans_attitude = sqlalchemy.Column(sqlalchemy.String)

    def __repr__(self):
        return f"<Friend> id: {self.bundle_id}; first_id: {self.first_id}; second_id: {self.second_id};" \
               f" mans_attitude: {self.mans_attitude}"
