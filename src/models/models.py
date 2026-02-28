"""
cinema-booking-app | src/models/models.py
SQLAlchemy ORM модельдері
"""

from datetime import datetime
from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey,
    Integer, Numeric, String, Text, UniqueConstraint, CheckConstraint
)
from src.database import Base


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String(50),  unique=True, nullable=False)
    email         = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name     = Column(String(100), nullable=False)
    phone         = Column(String(20))
    is_admin      = Column(Boolean, default=False)
    created_at    = Column(DateTime, default=datetime.utcnow)


class Movie(Base):
    __tablename__ = "movies"

    id           = Column(Integer, primary_key=True, index=True)
    title        = Column(String(200), nullable=False)
    description  = Column(Text)
    genre        = Column(String(50), nullable=False)
    duration_min = Column(Integer, nullable=False)
    rating       = Column(Numeric(3, 1))
    poster_url   = Column(String(500))
    release_date = Column(Date, nullable=False)
    is_active    = Column(Boolean, default=True)


class Hall(Base):
    __tablename__ = "halls"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(50), unique=True, nullable=False)
    total_seats   = Column(Integer, nullable=False)
    rows_count    = Column(Integer, nullable=False)
    seats_per_row = Column(Integer, nullable=False)


class Seat(Base):
    __tablename__ = "seats"
    __table_args__ = (
        UniqueConstraint("hall_id", "row_number", "seat_number"),
    )

    id          = Column(Integer, primary_key=True, index=True)
    hall_id     = Column(Integer, ForeignKey("halls.id", ondelete="CASCADE"), nullable=False)
    row_number  = Column(Integer, nullable=False)
    seat_number = Column(Integer, nullable=False)
    seat_type   = Column(String(20), default="standard")


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


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        UniqueConstraint("session_id", "seat_id"),
    )

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    seat_id    = Column(Integer, ForeignKey("seats.id"), nullable=False)
    status     = Column(String(20), default="booked")
    price_paid = Column(Numeric(8, 2), nullable=False)
    booked_at  = Column(DateTime, default=datetime.utcnow)
