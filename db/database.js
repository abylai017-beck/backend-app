// db/database.js - Дерекқор қосылымы және кестелер жасау

const Database = require('better-sqlite3');
const path = require('path');

// SQLite файлын ашу (жоқ болса өздігінен жасалады)
const db = new Database(path.join(__dirname, 'cinema.db'));

// Жылдам жұмыс үшін WAL режимін қосу
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON'); // Байланыстарды тексеру

// ============================================================
// КЕСТЕЛЕР ЖАСАУ (DDL - Data Definition Language)
// ============================================================

db.exec(`
  -- 1-кесте: ПАЙДАЛАНУШЫЛАР (users)
  CREATE TABLE IF NOT EXISTS users (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT    NOT NULL,
    email     TEXT    NOT NULL UNIQUE,   -- email қайталанбауы керек
    password  TEXT    NOT NULL,          -- bcrypt хэш
    role      TEXT    NOT NULL DEFAULT 'user', -- 'admin' немесе 'user'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  -- 2-кесте: ФИЛЬМДЕР (movies)
  CREATE TABLE IF NOT EXISTS movies (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    description TEXT,
    genre       TEXT    NOT NULL,
    duration    INTEGER NOT NULL,  -- минутпен
    poster_url  TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  -- 3-кесте: СЕАНСТАР (sessions) - фильм + уақыт + зал
  CREATE TABLE IF NOT EXISTS sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_id   INTEGER NOT NULL,
    hall       TEXT    NOT NULL,        -- 'Зал 1', 'Зал 2'
    date_time  DATETIME NOT NULL,       -- Сеанс уақыты
    price      REAL    NOT NULL,        -- Билет бағасы
    total_seats INTEGER NOT NULL DEFAULT 50,
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
  );

  -- 4-кесте: ОРЫНДАР (seats) - әр сеанстағы орындар
  CREATE TABLE IF NOT EXISTS seats (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    seat_number TEXT   NOT NULL,   -- 'A1', 'A2', 'B1'...
    is_booked  INTEGER NOT NULL DEFAULT 0,  -- 0=бос, 1=брондалған
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    UNIQUE(session_id, seat_number)  -- бір сеансда орын қайталанбайды
  );

  -- 5-кесте: БИЛЕТТЕР (tickets) - сатып алулар
  CREATE TABLE IF NOT EXISTS tickets (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    seat_id    INTEGER NOT NULL UNIQUE,  -- бір орын бір рет сатылады
    session_id INTEGER NOT NULL,
    total_price REAL   NOT NULL,
    status     TEXT    NOT NULL DEFAULT 'active', -- 'active', 'cancelled'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)    REFERENCES users(id),
    FOREIGN KEY (seat_id)    REFERENCES seats(id),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
  );
`);

console.log('✅ Дерекқор және кестелер дайын!');

module.exports = db;
