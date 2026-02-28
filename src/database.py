"""
cinema-booking-app | src/database.py
Дерекқор қосылымы — SQLAlchemy
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/cinema_db")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """SQLAlchemy ORM модельдері үшін базалық класс"""
    pass


def get_db():
    """FastAPI Depends() үшін дерекқор сессиясы"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
