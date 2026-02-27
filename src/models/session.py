"""
cinema-booking-app | src/models/session.py
Сеанс моделі — SQLAlchemy ORM
"""

from sqlalchemy import Column, Integer, Numeric, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base


class Session(Base):
    __tablename__ = "sessions"

    id             = Column(Integer, primary_key=True, index=True)
    movie_id       = Column(Integer, ForeignKey("movies.id"), nullable=False)
    hall_id        = Column(Integer, ForeignKey("halls.id"), nullable=False)
    start_time     = Column(DateTime, nullable=False)
    end_time       = Column(DateTime, nullable=False)
    price_standard = Column(Numeric(8, 2), nullable=False)
    price_vip      = Column(Numeric(8, 2), nullable=False)
    is_active      = Column(Boolean, default=True)

    movie   = relationship("Movie")
    hall    = relationship("Hall")
    tickets = relationship("Ticket", back_populates="session")

    def to_dict(self):
        return {
            "id":             self.id,
            "movie_id":       self.movie_id,
            "hall_id":        self.hall_id,
            "start_time":     str(self.start_time),
            "end_time":       str(self.end_time),
            "price_standard": float(self.price_standard),
            "price_vip":      float(self.price_vip),
            "is_active":      self.is_active,
        }
