"""
cinema-booking-app | src/models/movie.py
Фильм моделі — SQLAlchemy ORM
"""

from sqlalchemy import Column, Integer, String, Text, Numeric, Date, Boolean
from src.models.base import Base


class Movie(Base):
    __tablename__ = "movies"

    id           = Column(Integer, primary_key=True, index=True)
    title        = Column(String(200), nullable=False)
    description  = Column(Text, nullable=True)
    genre        = Column(String(50), nullable=False)
    duration_min = Column(Integer, nullable=False)
    rating       = Column(Numeric(3, 1), nullable=True)
    poster_url   = Column(String(500), nullable=True)
    release_date = Column(Date, nullable=False)
    is_active    = Column(Boolean, default=True)

    def to_dict(self):
        return {
            "id":           self.id,
            "title":        self.title,
            "description":  self.description,
            "genre":        self.genre,
            "duration_min": self.duration_min,
            "rating":       float(self.rating) if self.rating else None,
            "poster_url":   self.poster_url,
            "release_date": str(self.release_date),
            "is_active":    self.is_active,
        }
