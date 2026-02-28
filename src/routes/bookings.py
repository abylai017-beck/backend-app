"""
cinema-booking-app | src/routes/bookings.py
Брондау маршруттары
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.utils.schemas import BookingCreate, BookingOut, BookingUpdate
from src.controllers import bookings as ctrl

router = APIRouter(tags=["Bookings"])


@router.get("/sessions/{session_id}/seats")
def session_seats(session_id: int, db: Session = Depends(get_db)):
    """Сеанстағы барлық орындардың бос/бронды күйі"""
    return ctrl.get_seats_for_session(db, session_id)


@router.post("/bookings", response_model=BookingOut, status_code=201)
def book_ticket(data: BookingCreate, db: Session = Depends(get_db)):
    """Билет брондау"""
    return ctrl.create_booking(db, data)


@router.put("/bookings/{booking_id}", response_model=BookingOut)
def change_seat(booking_id: int, data: BookingUpdate, db: Session = Depends(get_db)):
    """Орынды ауыстыру"""
    return ctrl.update_booking(db, booking_id, data)


@router.delete("/bookings/{booking_id}")
def cancel_ticket(booking_id: int, db: Session = Depends(get_db)):
    """Броньды болдырмау"""
    return ctrl.cancel_booking(db, booking_id)
