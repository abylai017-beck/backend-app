"""
cinema-booking-app | src/routes/movies.py
Фильмдер маршруттары
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.controllers.movies_controller import (
    get_all_movies,
    get_movie_by_id,
    create_movie,
    update_movie,
    delete_movie,
)

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("/")
def list_movies(
    title: Optional[str] = Query(None, description="Атауы бойынша іздеу"),
    genre: Optional[str] = Query(None, description="Жанр бойынша сүзгі"),
    db: Session = Depends(get_db)
):
    """Фильмдер тізімі — іздеу және сүзгілеу мүмкіндігімен"""
    movies = get_all_movies(db, title=title, genre=genre)
    return [m.to_dict() for m in movies]


@router.get("/{movie_id}")
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    """Жеке фильм детальдары"""
    movie = get_movie_by_id(movie_id, db)
    return movie.to_dict()


@router.post("/", status_code=201)
def add_movie(data: dict, db: Session = Depends(get_db)):
    """Жаңа фильм қосу (тек әкімші)"""
    movie = create_movie(data, db)
    return movie.to_dict()


@router.put("/{movie_id}")
def edit_movie(movie_id: int, data: dict, db: Session = Depends(get_db)):
    """Фильм ақпаратын жаңарту"""
    movie = update_movie(movie_id, data, db)
    return movie.to_dict()


@router.delete("/{movie_id}", status_code=204)
def remove_movie(movie_id: int, db: Session = Depends(get_db)):
    """Фильмді архивке жіберу"""
    delete_movie(movie_id, db)
