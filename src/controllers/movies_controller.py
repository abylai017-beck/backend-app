"""
cinema-booking-app | src/controllers/movies_controller.py
Фильмдерге қатысты API логикасы
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session as DBSession

from src.models.movie import Movie
from src.utils.validators import validate_movie_data


def get_all_movies(db: DBSession, title: str = None, genre: str = None):
    """
    GET /movies
    Фильмдер тізімі — атауы немесе жанры бойынша сүзгілеу мүмкіндігімен
    """
    query = db.query(Movie).filter(Movie.is_active == True)

    if title:
        query = query.filter(Movie.title.ilike(f"%{title}%"))
    if genre:
        query = query.filter(Movie.genre == genre)

    return query.all()


def get_movie_by_id(movie_id: int, db: DBSession):
    """
    GET /movies/{id}
    Жеке фильм детальдары
    """
    movie = db.query(Movie).filter_by(id=movie_id, is_active=True).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм табылмады")
    return movie


def create_movie(data: dict, db: DBSession):
    """
    POST /movies
    Жаңа фильм қосу (тек әкімші)
    """
    validate_movie_data(data)

    movie = Movie(**data)
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


def update_movie(movie_id: int, data: dict, db: DBSession):
    """
    PUT /movies/{id}
    Фильм ақпаратын жаңарту
    """
    movie = db.query(Movie).filter_by(id=movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм табылмады")

    for field, value in data.items():
        if hasattr(movie, field) and value is not None:
            setattr(movie, field, value)

    db.commit()
    db.refresh(movie)
    return movie


def delete_movie(movie_id: int, db: DBSession):
    """
    DELETE /movies/{id}
    Фильмді архивке жіберу (soft delete — физикалық жоймайды)
    """
    movie = db.query(Movie).filter_by(id=movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм табылмады")

    movie.is_active = False
    db.commit()
