# Модель пользователя
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    chat_id = Column(Integer, unique=True)
    is_active = Column(Boolean, default=False)
    state = Column(String, default="unknown")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, chat_id={self.chat_id}, state={self.state})>"
