-- ============================================================
-- cinema-booking-app | schema.sql
-- Кестелерді құруға арналған DDL скрипттері
-- ============================================================

DROP TABLE IF EXISTS tickets  CASCADE;
DROP TABLE IF EXISTS seats    CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS movies   CASCADE;
DROP TABLE IF EXISTS halls    CASCADE;
DROP TABLE IF EXISTS users    CASCADE;

-- ------------------------------------------------------------
-- 1. users
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
-- 2. movies
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
-- 3. halls
-- ------------------------------------------------------------
CREATE TABLE halls (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(50) UNIQUE NOT NULL,
    total_seats   INTEGER NOT NULL CHECK (total_seats > 0),
    rows_count    INTEGER NOT NULL CHECK (rows_count > 0),
    seats_per_row INTEGER NOT NULL CHECK (seats_per_row > 0)
);

-- ------------------------------------------------------------
-- 4. seats
-- ------------------------------------------------------------
CREATE TABLE seats (
    id          SERIAL PRIMARY KEY,
    hall_id     INTEGER NOT NULL REFERENCES halls(id) ON DELETE CASCADE,
    row_number  INTEGER NOT NULL CHECK (row_number > 0),
    seat_number INTEGER NOT NULL CHECK (seat_number > 0),
    seat_type   VARCHAR(20) DEFAULT 'standard'
                CHECK (seat_type IN ('standard', 'vip', 'disabled')),
    UNIQUE (hall_id, row_number, seat_number)
);

-- ------------------------------------------------------------
-- 5. sessions
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

-- ✅ Залда сеанстар қабаттаспауы үшін trigger
CREATE OR REPLACE FUNCTION check_session_overlap()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM sessions
        WHERE hall_id   = NEW.hall_id
          AND id        != COALESCE(NEW.id, -1)
          AND is_active = TRUE
          AND start_time < NEW.end_time
          AND end_time   > NEW.start_time
    ) THEN
        RAISE EXCEPTION 'Залда осы уақытта басқа сеанс бар (hall_id=%, % – %)',
            NEW.hall_id, NEW.start_time, NEW.end_time;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_session_overlap
    BEFORE INSERT OR UPDATE ON sessions
    FOR EACH ROW EXECUTE FUNCTION check_session_overlap();

-- ------------------------------------------------------------
-- 6. tickets
-- ------------------------------------------------------------
CREATE TABLE tickets (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER      NOT NULL REFERENCES users(id),
    session_id INTEGER      NOT NULL REFERENCES sessions(id),
    seat_id    INTEGER      NOT NULL REFERENCES seats(id),
    status     VARCHAR(20)  DEFAULT 'booked'
               CHECK (status IN ('booked', 'paid', 'cancelled')),
    price_paid DECIMAL(8,2) NOT NULL CHECK (price_paid > 0),
    booked_at  TIMESTAMP    DEFAULT NOW(),
    UNIQUE (session_id, seat_id)
);

-- ------------------------------------------------------------
-- Индекстер
-- ------------------------------------------------------------
CREATE INDEX idx_sessions_start_time ON sessions(start_time);
CREATE INDEX idx_sessions_movie_id   ON sessions(movie_id);
CREATE INDEX idx_sessions_hall_id    ON sessions(hall_id);
CREATE INDEX idx_tickets_user_id     ON tickets(user_id);
CREATE INDEX idx_tickets_session_id  ON tickets(session_id);
CREATE INDEX idx_movies_genre        ON movies(genre);
CREATE INDEX idx_movies_is_active    ON movies(is_active);
