"""
cinema-booking-app | src/utils/validators.py
Деректерді тексеру — валидация функциялары
"""

from fastapi import HTTPException


def validate_booking_data(data: dict):
    """
    POST /bookings — міндетті өрістерді тексеру
    Фильм ID-і, орын нөмірі міндетті болуы тиіс
    """
    required_fields = ["user_id", "session_id", "seat_id"]

    # Міндетті өрістер бар ма?
    for field in required_fields:
        if field not in data or data[field] is None:
            raise HTTPException(
                status_code=422,
                detail=f"'{field}' міндетті өріс"
            )

    # ID мәндері оң сан болуы тиіс
    for field in required_fields:
        if not isinstance(data[field], int) or data[field] <= 0:
            raise HTTPException(
                status_code=422,
                detail=f"'{field}' 0-ден үлкен бүтін сан болуы тиіс"
            )


def validate_movie_data(data: dict):
    """
    POST /movies — міндетті өрістерді тексеру
    """
    required = ["title", "genre", "duration_min", "release_date"]

    for field in required:
        if field not in data or data[field] is None:
            raise HTTPException(
                status_code=422,
                detail=f"'{field}' міндетті өріс"
            )

    # Атау бос болмауы тиіс
    if not str(data.get("title", "")).strip():
        raise HTTPException(status_code=422, detail="Фильм атауы бос болмауы тиіс")

    # Ұзақтық оң сан
    if not isinstance(data.get("duration_min"), int) or data["duration_min"] <= 0:
        raise HTTPException(status_code=422, detail="duration_min 0-ден үлкен болуы тиіс")

    # Рейтинг 0–10 аралығында
    rating = data.get("rating")
    if rating is not None:
        if not (0 <= float(rating) <= 10):
            raise HTTPException(status_code=422, detail="rating 0 мен 10 арасында болуы тиіс")


def validate_update_booking(data: dict):
    """
    PUT /bookings/{id} — жаңарту деректерін тексеру
    """
    seat_id = data.get("seat_id")

    if seat_id is None:
        raise HTTPException(status_code=422, detail="'seat_id' міндетті өріс")

    if not isinstance(seat_id, int) or seat_id <= 0:
        raise HTTPException(status_code=422, detail="'seat_id' 0-ден үлкен бүтін сан болуы тиіс")
