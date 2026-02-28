"""
cinema-booking-app | src/main.py
FastAPI қосымшасының негізгі файлы
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes.movies import router as movies_router
from src.routes.bookings import router as bookings_router

app = FastAPI(
    title="Cinema Booking API",
    description="Кинотеатр билеттерін сату жүйесі",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(movies_router,   prefix="/api")
app.include_router(bookings_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Cinema Booking API жұмыс істеп тұр!",
        "version": "1.0.0",
        "docs":    "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
