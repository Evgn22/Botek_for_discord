import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Prefix(SqlAlchemyBase):
    __tablename__ = 'prefixs'

    server_id = sqlalchemy.Column(sqlalchemy.Integer,
                                  primary_key=True, autoincrement=True)
    server_name = sqlalchemy.Column(sqlalchemy.String)
    prefix = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    russian_ruletka = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

