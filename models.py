from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

# ТАБЛИЦЯ-ЗВ'ЯЗОК (Має бути перед класом User)
friendships = Table(
    "friendships",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("friend_id", Integer, ForeignKey("users.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    full_name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nuts_amount = Column(Integer, default=0)

    current_skin = Column(JSON, default=lambda: {"full_set": "regular", "background": "regular"})
    unlocked_skins = Column(JSON, default=lambda: ["full_regular", "bg_regular"])

    last_seen = Column(DateTime, onupdate=func.now())
    join_time = Column(DateTime, server_default=func.now())

    # Зв'язки
    friends = relationship(
        "User",
        secondary=friendships,
        primaryjoin=(id == friendships.c.user_id),
        secondaryjoin=(id == friendships.c.friend_id),
        backref="friend_of"
    )
    
    quests = relationship("Quest", back_populates="owner", cascade="all, delete-orphan", foreign_keys="[Quest.user_id]")
    sent_quests = relationship("Quest", back_populates="sender", foreign_keys="[Quest.sender_id]")


class Quest(Base):
    __tablename__ = "quests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    category = Column(String)
    from_who = Column(String) 
    
    is_started = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    difficulty = Column(Integer)
    base_reward = Column(Integer)

    deadlines_config = Column(JSON, nullable=True)
    multipliers_config = Column(JSON, nullable=True)
    selected_difficulty_level = Column(String)
    final_reward = Column(Integer, nullable=True)

    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Зовнішні ключі
    user_id = Column(Integer, ForeignKey("users.id"))
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    proof_data = Column(String, nullable=True)

    # Relationship
    owner = relationship("User", back_populates="quests", foreign_keys=[user_id])
    sender = relationship("User", back_populates="sent_quests", foreign_keys=[sender_id])