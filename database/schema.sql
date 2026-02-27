-- ============================================================
-- cinema-booking-app | schema.sql
-- Кестелерді құруға арналған DDL скрипттері
-- ============================================================

-- Алдымен бар кестелерді тазалау (тестілеу үшін)
DROP TABLE IF EXISTS tickets  CASCADE;
DROP TABLE IF EXISTS seats    CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS movies   CASCADE;
DROP TABLE IF EXISTS halls    CASCADE;
DROP TABLE IF EXISTS users    CASCADE;

-- ------------------------------------------------------------
-- 1. users — Пайдаланушылар
-- ------------------------------------------------------------
CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50)  UNIQUE NOT NULL,
    email         VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(100) NOT NULL,
    phone         VARCHAR(20),
    is_admin      BOOLEAN      DEFAULT FALSE,
    created_at    TIMESTAMP    DEFAULT NOW()
);

-- ------------------------------------------------------------
-- 2. movies — Фильмдер
-- ------------------------------------------------------------
CREATE TABLE movies (
    id           SERIAL PRIMARY KEY,
    title        VARCHAR(200) NOT NULL,
    description  TEXT,
    genre        VARCHAR(50)  NOT NULL,
    duration_min INTEGER      NOT NULL CHECK (duration_min > 0),
    rating       DECIMAL(3,1) CHECK (rating BETWEEN 0 AND 10),
    poster_url   VARCHAR(500),
    release_date DATE         NOT NULL,
    is_active    BOOLEAN      DEFAULT TRUE
);

-- ------------------------------------------------------------
-- 3. halls — Кинозалдар
-- ------------------------------------------------------------
CREATE TABLE halls (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(50) UNIQUE NOT NULL,
    total_seats   INTEGER NOT NULL CHECK (total_seats > 0),
    rows_count    INTEGER NOT NULL,
    seats_per_row INTEGER NOT NULL
);

-- ------------------------------------------------------------
-- 4. seats — Орындар
-- ------------------------------------------------------------
CREATE TABLE seats (
    id          SERIAL PRIMARY KEY,
    hall_id     INTEGER NOT NULL REFERENCES halls(id) ON DELETE CASCADE,
    row_number  INTEGER NOT NULL,
    seat_number INTEGER NOT NULL,
    seat_type   VARCHAR(20) DEFAULT 'standard'
                CHECK (seat_type IN ('standard', 'vip', 'disabled')),
    UNIQUE (hall_id, row_number, seat_number)
);

-- ------------------------------------------------------------
-- 5. sessions — Сеанстар кестесі
-- ------------------------------------------------------------
CREATE TABLE sessions (
    id             SERIAL PRIMARY KEY,
    movie_id       INTEGER      NOT NULL REFERENCES movies(id),
    hall_id        INTEGER      NOT NULL REFERENCES halls(id),
    start_time     TIMESTAMP    NOT NULL,
    end_time       TIMESTAMP    NOT NULL,
    price_standard DECIMAL(8,2) NOT NULL CHECK (price_standard > 0),
    price_vip      DECIMAL(8,2) NOT NULL CHECK (price_vip > 0),
    is_active      BOOLEAN      DEFAULT TRUE,
    CHECK (end_time > start_time)
);

-- ------------------------------------------------------------
-- 6. tickets — Билеттер
-- ------------------------------------------------------------
CREATE TABLE tickets (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER      NOT NULL REFERENCES users(id),
    session_id INTEGER      NOT NULL REFERENCES sessions(id),
    seat_id    INTEGER      NOT NULL REFERENCES seats(id),
    status     VARCHAR(20)  DEFAULT 'booked'
               CHECK (status IN ('booked', 'paid', 'cancelled')),
    price_paid DECIMAL(8,2) NOT NULL,
    booked_at  TIMESTAMP    DEFAULT NOW(),
    UNIQUE (session_id, seat_id)   -- Бір орынға екі билет болмайды
);

-- ------------------------------------------------------------
-- Индекстер — сұрауларды жылдамдату
-- ------------------------------------------------------------
CREATE INDEX idx_sessions_start_time ON sessions(start_time);
CREATE INDEX idx_sessions_movie_id   ON sessions(movie_id);
CREATE INDEX idx_tickets_user_id     ON tickets(user_id);
CREATE INDEX idx_tickets_session_id  ON tickets(session_id);
CREATE INDEX idx_movies_genre        ON movies(genre);
