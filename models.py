from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    full_name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    nuts_amount = Column(Integer, default=0)

    # Тепер це об'єкт: {"hat": "regular", "body": "regular", "eyes": "regular", ...}
    current_skin = Column(
        JSON, default=lambda: {"full_set": "regular", "background": "regular"}
    )
    # Список усіх куплених частин: ["hat_regular", "hat_golden", "body_regular"]
    unlocked_skins = Column(JSON, default=lambda: ["full_regular", "bg_regular"])

    last_seen = Column(DateTime, onupdate=func.now())
    join_time = Column(DateTime, server_default=func.now())

    quests = relationship("Quest", back_populates="owner", cascade="all, delete-orphan")


class Quest(Base):
    __tablename__ = "quests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    category = Column(String)
    from_who = Column(String)  # Від кого таска
    is_started = Column(Boolean, default=False)
    difficulty = Column(Integer)
    base_reward = Column(Integer)

    # Конфіги від Gemini
    # можна зберігати декілька для різної важкості
    deadlines_config = Column(JSON, nullable=True)
    multipliers_config = Column(JSON, nullable=True)

    # "easy", "medium" або "hard"
    selected_difficulty_level = Column(String)

    # Розрахований виграш (base_reward * multiplier).
    # Зберігаємо тут, щоб не рахувати кожен раз.
    final_reward = Column(Integer, nullable=True)

    is_completed = Column(Boolean, default=False)

    # Дата закінчення дедлайну (вибрана з config або встановлена вручну)
    deadline = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="quests")
