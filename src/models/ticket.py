"""
cinema-booking-app | src/models/ticket.py
Билет моделі — SQLAlchemy ORM
"""

from sqlalchemy import Column, Integer, Numeric, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.models.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    seat_id    = Column(Integer, ForeignKey("seats.id"), nullable=False)
    status     = Column(String(20), default="booked")
    price_paid = Column(Numeric(8, 2), nullable=False)
    booked_at  = Column(DateTime, server_default=func.now())

    user    = relationship("User", back_populates="tickets")
    session = relationship("Session", back_populates="tickets")
    seat    = relationship("Seat")

    def to_dict(self):
        return {
            "id":         self.id,
            "user_id":    self.user_id,
            "session_id": self.session_id,
            "seat_id":    self.seat_id,
            "status":     self.status,
            "price_paid": float(self.price_paid),
            "booked_at":  str(self.booked_at),
        }
