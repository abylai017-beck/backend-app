"""
cinema-booking-app | src/controllers/bookings.py
Брондауға қатысты бизнес-логика
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.models.models import Ticket, Seat, Session as CinemaSession
from src.utils.schemas import BookingCreate, BookingUpdate


def _get_session_or_404(db: Session, session_id: int) -> CinemaSession:
    session = db.query(CinemaSession).filter(
        CinemaSession.id == session_id,
        CinemaSession.is_active == True
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сеанс табылмады")
    return session


def _get_seat_or_404(db: Session, seat_id: int, hall_id: int) -> Seat:
    seat = db.query(Seat).filter(
        Seat.id == seat_id,
        Seat.hall_id == hall_id
    ).first()
    if not seat:
        raise HTTPException(status_code=404, detail="Орын осы залда жоқ")
    return seat


def _check_seat_available(db: Session, session_id: int, seat_id: int) -> None:
    """Орын бос па — тексеру"""
    existing = db.query(Ticket).filter(
        Ticket.session_id == session_id,
        Ticket.seat_id == seat_id,
        Ticket.status != "cancelled"
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Орын бос емес")


def _calc_price(cinema_session: CinemaSession, seat: Seat) -> float:
    return float(
        cinema_session.price_vip if seat.seat_type == "vip"
        else cinema_session.price_standard
    )


def get_seats_for_session(db: Session, session_id: int) -> list[dict]:
    cinema_session = _get_session_or_404(db, session_id)
    seats = db.query(Seat).filter(Seat.hall_id == cinema_session.hall_id).all()

    booked_ids = {
        t.seat_id for t in db.query(Ticket).filter(
            Ticket.session_id == session_id,
            Ticket.status != "cancelled"
        ).all()
    }

    return [
        {
            "id":          s.id,
            "hall_id":     s.hall_id,
            "row_number":  s.row_number,
            "seat_number": s.seat_number,
            "seat_type":   s.seat_type,
            "is_booked":   s.id in booked_ids,
        }
        for s in seats
    ]


def create_booking(db: Session, data: BookingCreate) -> Ticket:
    cinema_session = _get_session_or_404(db, data.session_id)
    seat = _get_seat_or_404(db, data.seat_id, cinema_session.hall_id)
    _check_seat_available(db, data.session_id, data.seat_id)

    price = _calc_price(cinema_session, seat)
    ticket = Ticket(
        user_id=data.user_id,
        session_id=data.session_id,
        seat_id=data.seat_id,
        price_paid=price,
        status="booked",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def update_booking(db: Session, booking_id: int, data: BookingUpdate) -> Ticket:
    """Орынды ауыстыру — ескі билетті болдырмай, жаңа орынға ауыстырады"""
    ticket = db.query(Ticket).filter(
        Ticket.id == booking_id,
        Ticket.status != "cancelled"
    ).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Бронь табылмады")

    cinema_session = _get_session_or_404(db, ticket.session_id)
    new_seat = _get_seat_or_404(db, data.seat_id, cinema_session.hall_id)
    _check_seat_available(db, ticket.session_id, data.seat_id)

    ticket.seat_id    = data.seat_id
    ticket.price_paid = _calc_price(cinema_session, new_seat)
    db.commit()
    db.refresh(ticket)
    return ticket


def cancel_booking(db: Session, booking_id: int) -> dict:
    ticket = db.query(Ticket).filter(Ticket.id == booking_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Бронь табылмады")
    if ticket.status == "cancelled":
        raise HTTPException(status_code=400, detail="Бронь бұрын болдырылмаған")

    ticket.status = "cancelled"
    db.commit()
    return {"detail": f"Бронь (id={booking_id}) болдырылмады"}
