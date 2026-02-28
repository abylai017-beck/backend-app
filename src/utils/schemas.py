"""
cinema-booking-app | src/utils/schemas.py
Pydantic схемалары — сұрау/жауап валидациясы
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


# ── Movies ──────────────────────────────────────────────────

class MovieBase(BaseModel):
    title:        str
    description:  Optional[str] = None
    genre:        str
    duration_min: int
    rating:       Optional[Decimal] = None
    poster_url:   Optional[str]     = None
    release_date: date

    @field_validator("duration_min")
    @classmethod
    def duration_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("duration_min нөлден үлкен болуы керек")
        return v

    @field_validator("rating")
    @classmethod
    def rating_range(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and not (0 <= v <= 10):
            raise ValueError("rating 0–10 аралығында болуы керек")
        return v


class MovieCreate(MovieBase):
    pass


class MovieUpdate(BaseModel):
    title:        Optional[str]     = None
    description:  Optional[str]     = None
    genre:        Optional[str]     = None
    duration_min: Optional[int]     = None
    rating:       Optional[Decimal] = None
    poster_url:   Optional[str]     = None
    release_date: Optional[date]    = None
    is_active:    Optional[bool]    = None


class MovieOut(MovieBase):
    id:        int
    is_active: bool

    model_config = {"from_attributes": True}


# ── Sessions ─────────────────────────────────────────────────

class SessionOut(BaseModel):
    id:             int
    movie_id:       int
    hall_id:        int
    start_time:     datetime
    end_time:       datetime
    price_standard: Decimal
    price_vip:      Decimal
    is_active:      bool

    model_config = {"from_attributes": True}


# ── Seats ────────────────────────────────────────────────────

class SeatOut(BaseModel):
    id:          int
    hall_id:     int
    row_number:  int
    seat_number: int
    seat_type:   str
    is_booked:   bool  # сеансқа байланысты есептеледі

    model_config = {"from_attributes": True}


# ── Bookings ─────────────────────────────────────────────────

class BookingCreate(BaseModel):
    user_id:    int
    session_id: int
    seat_id:    int


class BookingUpdate(BaseModel):
    seat_id: int  # тек орын ауыстыру


class BookingOut(BaseModel):
    id:         int
    user_id:    int
    session_id: int
    seat_id:    int
    status:     str
    price_paid: Decimal
    booked_at:  datetime

    model_config = {"from_attributes": True}
