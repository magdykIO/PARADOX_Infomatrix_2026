import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Creates db named 'messenger.db' in data/
DB_DIR = "./data"
DB_NAME = "messenger.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_DIR}/{DB_NAME}"

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    # * For Future
    import models
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

