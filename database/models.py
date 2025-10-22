from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    password=Column("password",String,nullable=False)
    favorites = relationship('Favorite', backref='user', lazy='subquery')


class Favorite(Base):
    __tablename__ = 'favorite'
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))
