from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List
import sqlite3, hashlib, secrets, os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cinema.db")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# БД 
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        username      TEXT    NOT NULL UNIQUE,
        email         TEXT    NOT NULL UNIQUE,
        password_hash TEXT    NOT NULL,
        password_salt TEXT    NOT NULL DEFAULT '',
        role          TEXT    NOT NULL DEFAULT 'user',
        token         TEXT,
        created_at    TEXT    DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS movies (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        title       TEXT    NOT NULL,
        description TEXT,
        genre       TEXT,
        duration    INTEGER NOT NULL DEFAULT 120,
        poster_url  TEXT,
        rating      REAL    DEFAULT 0.0,
        created_at  TEXT    DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS halls (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        name      TEXT    NOT NULL,
        rows      INTEGER NOT NULL DEFAULT 8,
        cols      INTEGER NOT NULL DEFAULT 10
    );
    CREATE TABLE IF NOT EXISTS sessions (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id   INTEGER NOT NULL,
        hall_id    INTEGER NOT NULL DEFAULT 1,
        start_time TEXT    NOT NULL,
        price      REAL    NOT NULL DEFAULT 1500.0,
        created_at TEXT    DEFAULT (datetime('now')),
        FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
        FOREIGN KEY (hall_id)  REFERENCES halls(id)  ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS tickets (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        user_id    INTEGER NOT NULL,
        seat_row   INTEGER NOT NULL,
        seat_col   INTEGER NOT NULL,
        status     TEXT    NOT NULL DEFAULT 'booked',
        created_at TEXT    DEFAULT (datetime('now')),
        FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
        UNIQUE (session_id, seat_row, seat_col)
    );
    """)
    if not db.execute("SELECT id FROM halls").fetchone():
        db.execute("INSERT INTO halls (name, rows, cols) VALUES ('Зал 1', 8, 10)")
        db.execute("INSERT INTO halls (name, rows, cols) VALUES ('Зал 2', 6, 12)")
        db.execute("INSERT INTO halls (name, rows, cols) VALUES ('VIP Зал', 5, 8)")
    if not db.execute("SELECT id FROM movies").fetchone():
        movies = [
            ("Дюна: Часть 2", "Продолжение эпической саги", "Фантастика", 166, "https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg", 8.5),
            ("Оппенгеймер", "История создателя атомной бомбы", "Драма/История", 180, "https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg", 8.9),
            ("Головоломка 2", "Новые эмоции Райли", "Анимация", 100, "https://image.tmdb.org/t/p/w500/vpnVM9B6NMmQpWeZvzLvDESb2QY.jpg", 7.9),
        ]
        for m in movies:
            db.execute("INSERT INTO movies (title,description,genre,duration,poster_url,rating) VALUES (?,?,?,?,?,?)", m)
        db.execute("INSERT INTO sessions (movie_id, hall_id, start_time, price) VALUES (1, 1, '2026-03-07 14:00', 2000)")
        db.execute("INSERT INTO sessions (movie_id, hall_id, start_time, price) VALUES (1, 2, '2026-03-07 18:00', 1800)")
        db.execute("INSERT INTO sessions (movie_id, hall_id, start_time, price) VALUES (2, 1, '2026-03-07 20:30', 2500)")
        db.execute("INSERT INTO sessions (movie_id, hall_id, start_time, price) VALUES (3, 3, '2026-03-08 12:00', 1500)")
    db.commit()
    db.close()
    yield

app = FastAPI(title="CinemaFlow API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
security = HTTPBearer(auto_error=False)

def hash_password(password: str, salt: str = None):
    if salt is None:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 260_000)
    return key.hex(), salt

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if not credentials:
        raise HTTPException(401, "Требуется авторизация")
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE token=?", (credentials.credentials,)).fetchone()
    db.close()
    if not user:
        raise HTTPException(401, "Недействительный токен")
    return dict(user)

def get_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(403, "Только для администраторов")
    return current_user

class RegisterModel(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: str    = Field(..., min_length=5)
    password: str = Field(..., min_length=6)

class LoginModel(BaseModel):
    username: str
    password: str

class MovieCreate(BaseModel):
    title:       str   = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    genre:       Optional[str] = None
    duration:    int   = Field(120, ge=1)
    poster_url:  Optional[str] = None
    rating:      float = Field(0.0, ge=0, le=10)

class HallCreate(BaseModel):
    name: str = Field(..., min_length=1)
    rows: int = Field(8, ge=1, le=20)
    cols: int = Field(10, ge=1, le=20)

class SessionCreate(BaseModel):
    movie_id:   int
    hall_id:    int   = 1
    start_time: str
    price:      float = Field(1500.0, ge=0)

class TicketBook(BaseModel):
    session_id: int
    seat_row:   int
    seat_col:   int

# Аутентификация
@app.post("/auth/register", tags=["Auth"])
async def register(data: RegisterModel):
    db = get_db()
    if db.execute("SELECT id FROM users WHERE username=? OR email=?", (data.username, data.email)).fetchone():
        raise HTTPException(400, "Пользователь уже существует")
    token = secrets.token_hex(32)
    pwd_hash, pwd_salt = hash_password(data.password)
    db.execute("INSERT INTO users (username,email,password_hash,password_salt,token) VALUES (?,?,?,?,?)",
               (data.username, data.email, pwd_hash, pwd_salt, token))
    db.commit()
    user = db.execute("SELECT id,username,role FROM users WHERE username=?", (data.username,)).fetchone()
    db.close()
    return {"message": "Регистрация успешна", "token": token, "user_id": user["id"],
            "username": user["username"], "role": user["role"]}

@app.post("/auth/login", tags=["Auth"])
async def login(data: LoginModel):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username=?", (data.username,)).fetchone()
    if not user:
        raise HTTPException(401, "Неверные данные")
    h, _ = hash_password(data.password, user["password_hash"] and user["password_salt"])
    stored, _ = hash_password(data.password, user["password_salt"])
    if stored != user["password_hash"]:
        raise HTTPException(401, "Неверные данные")
    token = secrets.token_hex(32)
    db.execute("UPDATE users SET token=? WHERE id=?", (token, user["id"]))
    db.commit()
    db.close()
    return {"message": "Вход выполнен", "token": token, "user_id": user["id"],
            "username": user["username"], "role": user["role"]}

@app.get("/auth/me", tags=["Auth"])
async def me(u=Depends(get_current_user)):
    return {"id": u["id"], "username": u["username"], "email": u["email"], "role": u["role"]}

@app.get("/movies", tags=["Movies"])
async def get_movies(genre: Optional[str] = None, search: Optional[str] = None):
    db = get_db()
    q = "SELECT * FROM movies WHERE 1=1"
    params = []
    if genre:  q += " AND genre LIKE ?"; params.append(f"%{genre}%")
    if search: q += " AND title LIKE ?"; params.append(f"%{search}%")
    q += " ORDER BY created_at DESC"
    movies = db.execute(q, params).fetchall()
    db.close()
    return [dict(m) for m in movies]

@app.get("/movies/{movie_id}", tags=["Movies"])
async def get_movie(movie_id: int):
    db = get_db()
    movie = db.execute("SELECT * FROM movies WHERE id=?", (movie_id,)).fetchone()
    db.close()
    if not movie: raise HTTPException(404, "Фильм не найден")
    return dict(movie)

@app.post("/movies", tags=["Movies"])
async def create_movie(data: MovieCreate, admin=Depends(get_admin)):
    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO movies (title,description,genre,duration,poster_url,rating) VALUES (?,?,?,?,?,?)",
                (data.title, data.description, data.genre, data.duration, data.poster_url, data.rating))
    db.commit()
    movie = db.execute("SELECT * FROM movies WHERE id=?", (cur.lastrowid,)).fetchone()
    db.close()
    return dict(movie)

@app.put("/movies/{movie_id}", tags=["Movies"])
async def update_movie(movie_id: int, data: MovieCreate, admin=Depends(get_admin)):
    db = get_db()
    if not db.execute("SELECT id FROM movies WHERE id=?", (movie_id,)).fetchone():
        raise HTTPException(404, "Фильм не найден")
    db.execute("UPDATE movies SET title=?,description=?,genre=?,duration=?,poster_url=?,rating=? WHERE id=?",
               (data.title, data.description, data.genre, data.duration, data.poster_url, data.rating, movie_id))
    db.commit()
    movie = db.execute("SELECT * FROM movies WHERE id=?", (movie_id,)).fetchone()
    db.close()
    return dict(movie)

@app.delete("/movies/{movie_id}", tags=["Movies"])
async def delete_movie(movie_id: int, admin=Depends(get_admin)):
    db = get_db()
    if not db.execute("SELECT id FROM movies WHERE id=?", (movie_id,)).fetchone():
        raise HTTPException(404, "Фильм не найден")
    db.execute("DELETE FROM movies WHERE id=?", (movie_id,))
    db.commit(); db.close()
    return {"status": "success", "deleted_id": movie_id}
@app.get("/halls", tags=["Halls"])
async def get_halls():
    db = get_db()
    halls = db.execute("SELECT * FROM halls").fetchall()
    db.close()
    return [dict(h) for h in halls]

@app.post("/halls", tags=["Halls"])
async def create_hall(data: HallCreate, admin=Depends(get_admin)):
    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO halls (name,rows,cols) VALUES (?,?,?)", (data.name, data.rows, data.cols))
    db.commit()
    hall = db.execute("SELECT * FROM halls WHERE id=?", (cur.lastrowid,)).fetchone()
    db.close()
    return dict(hall)

# ════════════════════════════════════════
#  SESSIONS
# ════════════════════════════════════════
@app.get("/sessions", tags=["Sessions"])
async def get_sessions(movie_id: Optional[int] = None):
    db = get_db()
    q = """SELECT s.*, m.title as movie_title, m.duration, m.poster_url, m.genre,
                  h.name as hall_name, h.rows, h.cols
           FROM sessions s
           JOIN movies m ON s.movie_id = m.id
           JOIN halls  h ON s.hall_id  = h.id
           WHERE 1=1"""
    params = []
    if movie_id: q += " AND s.movie_id=?"; params.append(movie_id)
    q += " ORDER BY s.start_time"
    sessions = db.execute(q, params).fetchall()
    db.close()
    return [dict(s) for s in sessions]

@app.get("/sessions/{session_id}", tags=["Sessions"])
async def get_session(session_id: int):
    db = get_db()
    s = db.execute("""SELECT s.*, m.title as movie_title, m.duration, m.poster_url,
                             h.name as hall_name, h.rows, h.cols
                      FROM sessions s
                      JOIN movies m ON s.movie_id=m.id
                      JOIN halls  h ON s.hall_id=h.id
                      WHERE s.id=?""", (session_id,)).fetchone()
    db.close()
    if not s: raise HTTPException(404, "Сеанс не найден")
    return dict(s)

@app.post("/sessions", tags=["Sessions"])
async def create_session(data: SessionCreate, admin=Depends(get_admin)):
    db = get_db()
    if not db.execute("SELECT id FROM movies WHERE id=?", (data.movie_id,)).fetchone():
        raise HTTPException(404, "Фильм не найден")
    cur = db.cursor()
    cur.execute("INSERT INTO sessions (movie_id,hall_id,start_time,price) VALUES (?,?,?,?)",
                (data.movie_id, data.hall_id, data.start_time, data.price))
    db.commit()
    s = db.execute("""SELECT s.*, m.title as movie_title, h.name as hall_name, h.rows, h.cols
                      FROM sessions s JOIN movies m ON s.movie_id=m.id JOIN halls h ON s.hall_id=h.id
                      WHERE s.id=?""", (cur.lastrowid,)).fetchone()
    db.close()
    return dict(s)

@app.delete("/sessions/{session_id}", tags=["Sessions"])
async def delete_session(session_id: int, admin=Depends(get_admin)):
    db = get_db()
    if not db.execute("SELECT id FROM sessions WHERE id=?", (session_id,)).fetchone():
        raise HTTPException(404, "Сеанс не найден")
    db.execute("DELETE FROM sessions WHERE id=?", (session_id,))
    db.commit(); db.close()
    return {"status": "success", "deleted_id": session_id}

# ════════════════════════════════════════
#  SEATS  (занятые места для сеанса)
# ════════════════════════════════════════
@app.get("/sessions/{session_id}/seats", tags=["Seats"])
async def get_seats(session_id: int):
    db = get_db()
    s = db.execute("""SELECT s.id, h.rows, h.cols FROM sessions s
                      JOIN halls h ON s.hall_id=h.id WHERE s.id=?""", (session_id,)).fetchone()
    if not s: raise HTTPException(404, "Сеанс не найден")
    booked = db.execute("SELECT seat_row, seat_col FROM tickets WHERE session_id=?", (session_id,)).fetchall()
    db.close()
    booked_set = {(r["seat_row"], r["seat_col"]) for r in booked}
    seats = []
    for row in range(1, s["rows"] + 1):
        for col in range(1, s["cols"] + 1):
            seats.append({"row": row, "col": col,
                          "status": "booked" if (row, col) in booked_set else "free"})
    return {"session_id": session_id, "rows": s["rows"], "cols": s["cols"], "seats": seats}

# ════════════════════════════════════════
#  TICKETS
# ════════════════════════════════════════
@app.post("/tickets", tags=["Tickets"])
async def book_ticket(data: TicketBook, u=Depends(get_current_user)):
    db = get_db()
    s = db.execute("SELECT s.*, h.rows, h.cols FROM sessions s JOIN halls h ON s.hall_id=h.id WHERE s.id=?",
                   (data.session_id,)).fetchone()
    if not s: raise HTTPException(404, "Сеанс не найден")
    if not (1 <= data.seat_row <= s["rows"] and 1 <= data.seat_col <= s["cols"]):
        raise HTTPException(400, f"Неверное место. Зал: {s['rows']} рядов x {s['cols']} мест")
    if db.execute("SELECT id FROM tickets WHERE session_id=? AND seat_row=? AND seat_col=?",
                  (data.session_id, data.seat_row, data.seat_col)).fetchone():
        raise HTTPException(400, "Место уже занято")
    cur = db.cursor()
    cur.execute("INSERT INTO tickets (session_id,user_id,seat_row,seat_col) VALUES (?,?,?,?)",
                (data.session_id, u["id"], data.seat_row, data.seat_col))
    db.commit()
    ticket = db.execute("""SELECT t.*, s.start_time, s.price, m.title as movie_title,
                                  h.name as hall_name
                           FROM tickets t
                           JOIN sessions s ON t.session_id=s.id
                           JOIN movies m   ON s.movie_id=m.id
                           JOIN halls h    ON s.hall_id=h.id
                           WHERE t.id=?""", (cur.lastrowid,)).fetchone()
    db.close()
    return dict(ticket)

@app.get("/tickets/my", tags=["Tickets"])
async def my_tickets(u=Depends(get_current_user)):
    db = get_db()
    tickets = db.execute("""SELECT t.*, s.start_time, s.price, m.title as movie_title,
                                   m.poster_url, h.name as hall_name
                            FROM tickets t
                            JOIN sessions s ON t.session_id=s.id
                            JOIN movies m   ON s.movie_id=m.id
                            JOIN halls h    ON s.hall_id=h.id
                            WHERE t.user_id=?
                            ORDER BY t.created_at DESC""", (u["id"],)).fetchall()
    db.close()
    return [dict(t) for t in tickets]

@app.delete("/tickets/{ticket_id}", tags=["Tickets"])
async def cancel_ticket(ticket_id: int, u=Depends(get_current_user)):
    db = get_db()
    ticket = db.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone()
    if not ticket: raise HTTPException(404, "Билет не найден")
    if ticket["user_id"] != u["id"] and u["role"] != "admin":
        raise HTTPException(403, "Нет доступа")
    db.execute("DELETE FROM tickets WHERE id=?", (ticket_id,))
    db.commit(); db.close()
    return {"status": "success", "cancelled_id": ticket_id}

@app.get("/tickets/all", tags=["Tickets"])
async def all_tickets(admin=Depends(get_admin)):
    db = get_db()
    tickets = db.execute("""SELECT t.*, u.username, s.start_time, s.price,
                                   m.title as movie_title, h.name as hall_name
                            FROM tickets t
                            JOIN users u    ON t.user_id=u.id
                            JOIN sessions s ON t.session_id=s.id
                            JOIN movies m   ON s.movie_id=m.id
                            JOIN halls h    ON s.hall_id=h.id
                            ORDER BY t.created_at DESC""").fetchall()
    db.close()
    return [dict(t) for t in tickets]

# ════════════════════════════════════════
#  ADMIN — make admin
# ════════════════════════════════════════
@app.post("/auth/make-admin/{user_id}", tags=["Auth"])
async def make_admin(user_id: int, admin=Depends(get_admin)):
    db = get_db()
    db.execute("UPDATE users SET role='admin' WHERE id=?", (user_id,))
    db.commit(); db.close()
    return {"status": "success", "message": f"User {user_id} is now admin"}

# ════════════════════════════════════════
#  FRONTEND
# ════════════════════════════════════════
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def frontend():
    p = os.path.join(BASE_DIR, "index.html")
    return open(p, encoding="utf-8").read() if os.path.exists(p) else "<h1>index.html not found</h1>"

@app.get("/style.css", include_in_schema=False)
async def css():
    return FileResponse(os.path.join(BASE_DIR, "style.css"), media_type="text/css")

@app.get("/script.js", include_in_schema=False)
async def js():
    return FileResponse(os.path.join(BASE_DIR, "script.js"), media_type="application/javascript")
