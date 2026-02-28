"""
cinema-booking-app | src/controllers/movies.py
Фильмдерге қатысты бизнес-логика
"""

from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.models.models import Movie
from src.utils.schemas import MovieCreate, MovieUpdate


def get_all_movies(
    db: Session,
    title: Optional[str] = None,
    genre: Optional[str] = None,
) -> list[Movie]:
    query = db.query(Movie).filter(Movie.is_active == True)
    if title:
        query = query.filter(Movie.title.ilike(f"%{title}%"))
    if genre:
        query = query.filter(Movie.genre.ilike(f"%{genre}%"))
    return query.all()


def get_movie_by_id(db: Session, movie_id: int) -> Movie:
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм табылмады")
    return movie


def create_movie(db: Session, data: MovieCreate) -> Movie:
    movie = Movie(**data.model_dump())
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


def update_movie(db: Session, movie_id: int, data: MovieUpdate) -> Movie:
    movie = get_movie_by_id(db, movie_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(movie, field, value)
    db.commit()
    db.refresh(movie)
    return movie


def archive_movie(db: Session, movie_id: int) -> dict:
    """Фильмді өшірмей, is_active=False қылып архивке жібереді"""
    movie = get_movie_by_id(db, movie_id)
    movie.is_active = False
    db.commit()
    return {"detail": f"Фильм (id={movie_id}) архивке жіберілді"}
