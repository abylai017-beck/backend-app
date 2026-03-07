# 🎬 CinemaFlow — Cinema Booking App

**Stack:** Python · FastAPI · SQLite/PostgreSQL · HTML/CSS/JS

---

## 🚀 Запуск проекта

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Запустить сервер
uvicorn src.main:app --reload
```

Сервер: http://127.0.0.1:8000  
Swagger UI: http://127.0.0.1:8000/docs  
Frontend: открыть `index.html` в браузере

---

## 📡 Тестирование через Postman

### Базовый URL
```
http://127.0.0.1:8000
```

---

### 1. Проверка сервера

**GET** `/health`

```
GET http://127.0.0.1:8000/health
```

**Ожидаемый ответ:**
```json
{
  "status": "ok"
}
```

---

### 2. Фильмы

#### Получить все фильмы
**GET** `/api/movies/`

```
GET http://127.0.0.1:8000/api/movies/
```

**Ожидаемый ответ:**
```json
[
  {
    "id": 1,
    "title": "Dune: Part 2",
    "genre": "Sci-Fi",
    "duration_min": 166,
    "rating": "8.5",
    "release_date": "2024-03-01",
    "is_active": true
  }
]
```

---

#### Поиск по названию
**GET** `/api/movies/?title=Dune`

```
GET http://127.0.0.1:8000/api/movies/?title=Dune
```

---

#### Фильтр по жанру
**GET** `/api/movies/?genre=Thriller`

```
GET http://127.0.0.1:8000/api/movies/?genre=Thriller
```

---

#### Получить фильм по ID
**GET** `/api/movies/{id}`

```
GET http://127.0.0.1:8000/api/movies/1
```

---

#### Добавить фильм
**POST** `/api/movies/`

```
POST http://127.0.0.1:8000/api/movies/
Content-Type: application/json
```

**Body (raw → JSON):**
```json
{
  "title": "Interstellar",
  "description": "A team of explorers travel through a wormhole in space.",
  "genre": "Sci-Fi",
  "duration_min": 169,
  "rating": 8.6,
  "poster_url": "https://example.com/poster.jpg",
  "release_date": "2014-11-07"
}
```

**Ожидаемый ответ:** `201 Created`
```json
{
  "id": 5,
  "title": "Interstellar",
  "is_active": true,
  ...
}
```

---

#### Обновить фильм
**PUT** `/api/movies/{id}`

```
PUT http://127.0.0.1:8000/api/movies/1
Content-Type: application/json
```

**Body (raw → JSON):**
```json
{
  "rating": 9.0,
  "description": "Updated description"
}
```

---

#### Архивировать фильм (мягкое удаление)
**DELETE** `/api/movies/{id}`

```
DELETE http://127.0.0.1:8000/api/movies/1
```

**Ожидаемый ответ:**
```json
{
  "detail": "Film (id=1) archived"
}
```

---

### 3. Сеансы и места

#### Получить места сеанса
**GET** `/api/sessions/{id}/seats`

```
GET http://127.0.0.1:8000/api/sessions/1/seats
```

**Ожидаемый ответ:**
```json
[
  {
    "id": 1,
    "hall_id": 1,
    "row_number": 1,
    "seat_number": 1,
    "seat_type": "vip",
    "is_booked": true
  },
  {
    "id": 3,
    "hall_id": 1,
    "row_number": 1,
    "seat_number": 3,
    "seat_type": "vip",
    "is_booked": false
  }
]
```

---

### 4. Брони (Bookings)

#### Забронировать билет
**POST** `/api/bookings`

```
POST http://127.0.0.1:8000/api/bookings
Content-Type: application/json
```

**Body (raw → JSON):**
```json
{
  "user_id": 2,
  "session_id": 1,
  "seat_id": 5
}
```

**Ожидаемый ответ:** `201 Created`
```json
{
  "id": 4,
  "user_id": 2,
  "session_id": 1,
  "seat_id": 5,
  "status": "booked",
  "price_paid": "4500.00",
  "booked_at": "2025-07-01T10:00:00"
}
```

**Если место занято — ответ** `409 Conflict`:
```json
{
  "detail": "Seat is not available"
}
```

---

#### Сменить место
**PUT** `/api/bookings/{id}`

```
PUT http://127.0.0.1:8000/api/bookings/1
Content-Type: application/json
```

**Body (raw → JSON):**
```json
{
  "seat_id": 10
}
```

---

#### Отменить бронь
**DELETE** `/api/bookings/{id}`

```
DELETE http://127.0.0.1:8000/api/bookings/1
```

**Ожидаемый ответ:**
```json
{
  "detail": "Booking (id=1) cancelled"
}
```

---

## ⚠️ Коды ответов

| Код | Значение |
|-----|----------|
| 200 | Успешно |
| 201 | Создано |
| 404 | Не найдено |
| 409 | Конфликт (место занято) |
| 422 | Ошибка валидации данных |

---

## 🗄️ База данных

```
movies   (1) ──── (N) sessions
halls    (1) ──── (N) seats
halls    (1) ──── (N) sessions
sessions (1) ──── (N) tickets
seats    (1) ──── (N) tickets
users    (1) ──── (N) tickets
```

---

## 👥 Команда

| Студент | GitHub | Роль |
|---------|--------|------|
| 1-студент | @username1 | Backend, API |
| 2-студент | @username2 | База данных, деплой |
| 3-студент | @username3 | Тестирование |
