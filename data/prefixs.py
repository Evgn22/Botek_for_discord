import sqlalchemy
from .db_session import SqlAlchemyBase


class Prefix(SqlAlchemyBase):
    __tablename__ = 'prefixs'

    server_id = sqlalchemy.Column(sqlalchemy.Integer,
                                  primary_key=True, autoincrement=True)
    server_name = sqlalchemy.Column(sqlalchemy.String)
    prefix = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    mafia = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    players = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    chat = sqlalchemy.Column(sqlalchemy.String, nullable=True)

