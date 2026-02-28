"""
cinema-booking-app | src/routes/movies.py
Фильмдер маршруттары
"""

from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.utils.schemas import MovieCreate, MovieOut, MovieUpdate
from src.controllers import movies as ctrl

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("/", response_model=list[MovieOut])
def list_movies(
    title: Optional[str] = None,
    genre: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Фильмдер тізімі. title немесе genre бойынша сүзгі қолдануға болады."""
    return ctrl.get_all_movies(db, title=title, genre=genre)


@router.get("/{movie_id}", response_model=MovieOut)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    """Фильм детальдары"""
    return ctrl.get_movie_by_id(db, movie_id)


@router.post("/", response_model=MovieOut, status_code=201)
def add_movie(data: MovieCreate, db: Session = Depends(get_db)):
    """Жаңа фильм қосу"""
    return ctrl.create_movie(db, data)


@router.put("/{movie_id}", response_model=MovieOut)
def edit_movie(movie_id: int, data: MovieUpdate, db: Session = Depends(get_db)):
    """Фильм ақпаратын жаңарту"""
    return ctrl.update_movie(db, movie_id, data)


@router.delete("/{movie_id}")
def remove_movie(movie_id: int, db: Session = Depends(get_db)):
    """Фильмді архивке жіберу (өшірмейді)"""
    return ctrl.archive_movie(db, movie_id)
