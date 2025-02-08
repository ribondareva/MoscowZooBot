# Модель отзывов
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from bot.models.animals import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    username = Column(String, nullable=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Feedback {self.id} from {self.username}>"
