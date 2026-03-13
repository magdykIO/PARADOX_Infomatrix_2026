from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, unique=True, index=True)

    full_name = Column(String, unique=False, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)

    hashed_password = Column(String, nullable=False)

    last_seen = Column(DateTime, onupdate=func.now())  # When user's info changes in db
    join_time = Column(DateTime, server_default=func.now())  # When user signed up

    # Зв'язок з квестами: один юзер має багато квестів
    quests = relationship("Quest", back_populates="owner", cascade="all, delete-orphan")


class Quest(Base):
    __tablename__ = "quests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)  # Назва таски
    category = Column(String)  # Daily, Learn Matan, History тощо
    nuts_reward = Column(Integer)  # Кількість горішків (+1 на фото)

    is_completed = Column(Boolean, default=False)  # Виконано чи ні
    deadline = Column(DateTime, nullable=True)  # Коли таска згорає
    created_at = Column(DateTime, server_default=func.now())

    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="quests")
