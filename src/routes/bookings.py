"""
cinema-booking-app | src/routes/bookings.py
Брондау және сеанс маршруттары
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.controllers.bookings_controller import (
    get_session_seats,
    create_booking,
    update_booking,
    cancel_booking,
)

router = APIRouter(tags=["Bookings"])


@router.get("/sessions/{session_id}/seats")
def seats_availability(session_id: int, db: Session = Depends(get_db)):
    """
    Орын таңдау — сеанстың барлық орындарын бос/бронды күйімен қайтарады
    """
    return get_session_seats(session_id, db)


@router.post("/bookings", status_code=201)
def book_ticket(data: dict, db: Session = Depends(get_db)):
    """
    Билет брондау
    Міндетті өрістер: user_id, session_id, seat_id
    """
    ticket = create_booking(data, db)
    return ticket.to_dict()


@router.put("/bookings/{booking_id}")
def change_seat(booking_id: int, data: dict, db: Session = Depends(get_db)):
    """
    Орынды ауыстыру
    Міндетті өріс: seat_id (жаңа орын)
    """
    ticket = update_booking(booking_id, data, db)
    return ticket.to_dict()


@router.delete("/bookings/{booking_id}", status_code=204)
def cancel(booking_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Броньды болдырмау — тек өз билетін болдырмай алады
    """
    cancel_booking(booking_id, user_id=user_id, db=db)
