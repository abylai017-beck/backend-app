"""
cinema-booking-app | src/controllers/bookings_controller.py
Билет брондауға қатысты API логикасы
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session as DBSession

from src.models.ticket import Ticket
from src.models.session import Session
from src.models.seat import Seat
from src.utils.validators import validate_booking_data


def get_session_seats(session_id: int, db: DBSession):
    """
    GET /sessions/{id}/seats
    Орын таңдау логикасы — бос және бронды орындарды қайтарады
    """
    session = db.query(Session).filter_by(id=session_id, is_active=True).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сеанс табылмады")

    all_seats = db.query(Seat).filter_by(hall_id=session.hall_id).all()

    # Брондалған орын ID-лерін жинау
    booked_seat_ids = {
        t.seat_id for t in db.query(Ticket).filter(
            Ticket.session_id == session_id,
            Ticket.status.in_(["booked", "paid"])
        ).all()
    }

    return [
        {
            "seat_id":      seat.id,
            "row":          seat.row_number,
            "seat_number":  seat.seat_number,
            "type":         seat.seat_type,
            "is_available": seat.id not in booked_seat_ids,
            "price": (
                float(session.price_vip)
                if seat.seat_type == "vip"
                else float(session.price_standard)
            )
        }
        for seat in all_seats
    ]


def create_booking(data: dict, db: DBSession):
    """
    POST /bookings
    Билет брондау — орын бос екенін тексереді
    """
    validate_booking_data(data)

    # 1. Сеанс бар және белсенді ме?
    session = db.query(Session).filter_by(
        id=data["session_id"], is_active=True
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сеанс табылмады")

    # 2. Орын осы залда бар ма?
    seat = db.query(Seat).filter_by(
        id=data["seat_id"], hall_id=session.hall_id
    ).first()
    if not seat:
        raise HTTPException(status_code=404, detail="Орын табылмады")

    # 3. Орын бос па?
    existing = db.query(Ticket).filter(
        Ticket.session_id == data["session_id"],
        Ticket.seat_id    == data["seat_id"],
        Ticket.status.in_(["booked", "paid"])
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Бұл орын бұрыннан бронды")

    # 4. Орын типіне қарай баға анықтау
    price = (
        session.price_vip
        if seat.seat_type == "vip"
        else session.price_standard
    )

    # 5. Билет жасау
    ticket = Ticket(
        user_id    = data["user_id"],
        session_id = data["session_id"],
        seat_id    = data["seat_id"],
        price_paid = price,
        status     = "booked"
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def update_booking(booking_id: int, data: dict, db: DBSession):
    """
    PUT /bookings/{id}
    Орынды ауыстыру
    """
    ticket = db.query(Ticket).filter_by(id=booking_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Брон табылмады")

    if ticket.status == "paid":
        raise HTTPException(status_code=400,
                            detail="Төленген броньды өзгертуге болмайды")

    new_seat_id = data.get("seat_id")
    if not new_seat_id:
        raise HTTPException(status_code=422, detail="seat_id міндетті өріс")

    # Жаңа орын бос па?
    conflict = db.query(Ticket).filter(
        Ticket.session_id == ticket.session_id,
        Ticket.seat_id    == new_seat_id,
        Ticket.status.in_(["booked", "paid"])
    ).first()
    if conflict:
        raise HTTPException(status_code=409, detail="Таңдалған орын бос емес")

    ticket.seat_id = new_seat_id
    db.commit()
    db.refresh(ticket)
    return ticket


def cancel_booking(booking_id: int, user_id: int, db: DBSession):
    """
    DELETE /bookings/{id}
    Броньды болдырмау
    """
    ticket = db.query(Ticket).filter_by(
        id=booking_id, user_id=user_id
    ).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Брон табылмады")

    if ticket.status == "paid":
        raise HTTPException(status_code=400,
                            detail="Төленген билетті болдырмау мүмкін емес")

    ticket.status = "cancelled"
    db.commit()
