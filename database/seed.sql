-- ============================================================
-- cinema-booking-app | seed.sql
-- Тестілік деректерді толтыру скрипттері
-- ============================================================

-- ------------------------------------------------------------
-- Кинозалдар
-- ------------------------------------------------------------
INSERT INTO halls (name, total_seats, rows_count, seats_per_row) VALUES
    ('Зал 1',      100, 10, 10),
    ('Зал 2 VIP',   60,  6, 10),
    ('IMAX Зал',   200, 20, 10);

-- ------------------------------------------------------------
-- Орындар — Зал 1 (қатар 1-2 VIP, қалғаны standard)
-- ------------------------------------------------------------
INSERT INTO seats (hall_id, row_number, seat_number, seat_type)
SELECT
    1, r, s,
    CASE WHEN r <= 2 THEN 'vip' ELSE 'standard' END
FROM generate_series(1, 10) AS r,
     generate_series(1, 10) AS s;

-- Зал 2 VIP (барлығы VIP)
INSERT INTO seats (hall_id, row_number, seat_number, seat_type)
SELECT 2, r, s, 'vip'
FROM generate_series(1, 6) AS r,
     generate_series(1, 10) AS s;

-- IMAX Зал (барлығы standard)
INSERT INTO seats (hall_id, row_number, seat_number, seat_type)
SELECT 3, r, s, 'standard'
FROM generate_series(1, 20) AS r,
     generate_series(1, 10) AS s;

-- ------------------------------------------------------------
-- Фильмдер
-- ------------------------------------------------------------
INSERT INTO movies (title, description, genre, duration_min, rating, release_date) VALUES
    ('Дюна: Бөлім 2',
     'Пол Атрейдес фримендермен бірігіп Харконненге қарсы күреседі.',
     'Ғылыми фантастика', 166, 8.5, '2024-03-01'),

    ('Бүгін түнде',
     'Детектив бір түнде қаланың сырын ашуға тырысады.',
     'Триллер', 112, 7.2, '2024-04-15'),

    ('Каруана',
     'Достар арасындағы күлкілі жағдайлар туралы комедия.',
     'Комедия', 98, 6.8, '2024-05-20'),

    ('Жел ізімен',
     'Ауыл жігіті қалада өз жолын іздейді.',
     'Драма', 138, 9.1, '2024-02-10');

-- ------------------------------------------------------------
-- Сеанстар
-- ------------------------------------------------------------
INSERT INTO sessions (movie_id, hall_id, start_time, end_time, price_standard, price_vip) VALUES
    (1, 1, '2025-07-01 10:00', '2025-07-01 12:46', 2500.00, 4500.00),
    (1, 1, '2025-07-01 14:00', '2025-07-01 16:46', 2500.00, 4500.00),
    (1, 3, '2025-07-01 18:00', '2025-07-01 20:46', 3500.00, 3500.00),
    (2, 2, '2025-07-01 13:00', '2025-07-01 14:52', 3500.00, 6000.00),
    (3, 1, '2025-07-02 11:00', '2025-07-02 12:38', 2000.00, 3500.00),
    (4, 2, '2025-07-02 16:00', '2025-07-02 18:18', 3000.00, 5000.00);

-- ------------------------------------------------------------
-- Тест пайдаланушылары
-- Ескерту: нақты жүйеде құпия сөзді app арқылы хэштеңіз
-- (passlib: pwd_context.hash("password123"))
-- ------------------------------------------------------------
INSERT INTO users (username, email, password_hash, full_name, is_admin) VALUES
    ('admin',   'admin@cinema.kz',  '$2b$12$hashplaceholder1', 'Жүйе Әкімшісі', TRUE),
    ('aibek',   'aibek@mail.kz',    '$2b$12$hashplaceholder2', 'Айбек Сейіт',   FALSE),
    ('gulnara', 'gulnara@mail.kz',  '$2b$12$hashplaceholder3', 'Гүлнара Асан',  FALSE);

-- ------------------------------------------------------------
-- Тест билеттері
-- ✅ seat_id — SERIAL болғандықтан нақты id-ді subquery арқылы аламыз
-- ------------------------------------------------------------
INSERT INTO tickets (user_id, session_id, seat_id, status, price_paid)
SELECT 2, 1, s.id, 'booked', 4500.00
FROM seats s WHERE s.hall_id = 1 AND s.row_number = 1 AND s.seat_number = 1;

INSERT INTO tickets (user_id, session_id, seat_id, status, price_paid)
SELECT 2, 1, s.id, 'booked', 4500.00
FROM seats s WHERE s.hall_id = 1 AND s.row_number = 1 AND s.seat_number = 2;

INSERT INTO tickets (user_id, session_id, seat_id, status, price_paid)
SELECT 3, 1, s.id, 'paid', 2500.00
FROM seats s WHERE s.hall_id = 1 AND s.row_number = 3 AND s.seat_number = 1;
