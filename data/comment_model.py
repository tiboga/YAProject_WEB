import sqlalchemy
from .db_session import SqlAlchemyBase


class Comment(SqlAlchemyBase):
    __tablename__ = 'comment'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    comment_text = sqlalchemy.Column(sqlalchemy.TEXT, nullable=False)
    state_of_comment = sqlalchemy.Column(sqlalchemy.TEXT, nullable=False)
