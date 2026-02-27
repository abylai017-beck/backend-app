# 🎬 Cinema Booking App

**Кинотеатр билеттерін сату жүйесі** — Фильмдер кестесі және орындарды таңдау логикасы

---

## 📋 Жоба туралы

Бұл жоба Backend және дерекқорларға кіріспе пәні бойынша топтық тапсырма.  
Пайдаланушылар фильмдер мен сеанстарды қарай алады, орын таңдай алады және билет брондай алады.

**Стек:** Python · FastAPI · PostgreSQL · SQLAlchemy

---

## 📁 Жоба құрылымы

```
cinema-booking-app/
├── database/
│   ├── schema.sql       # Кестелерді құруға арналған DDL скрипттері
│   └── seed.sql         # Тестілік деректерді толтыру скрипттері
├── src/
│   ├── controllers/     # API эндпоинттарын өңдеу логикасы
│   ├── models/          # Деректер модельдері (SQLAlchemy ORM)
│   ├── routes/          # Маршруттар (URL эндпоинттары)
│   ├── utils/           # Валидация және көмекші функциялар
│   ├── database.py      # Дерекқор қосылымы
│   └── main.py          # FastAPI негізгі файлы
├── docs/
│   └── erd_diagram.pdf  # Дерекқор схемасы (ER-диаграмма)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Іске қосу

### 1. Репозиторийді клондау
```bash
git clone https://github.com/[команда]/cinema-booking-app.git
cd cinema-booking-app
```

### 2. Виртуалды орта жасау
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. `.env` файлын баптау
```bash
cp .env.example .env
# .env файлын ашып, мәндерді толтырыңыз
```

`.env` мазмұны:
```
DATABASE_URL=postgresql://user:password@localhost:5432/cinema_db
```

### 4. Дерекқорды баптау
```bash
psql -U postgres -d cinema_db -f database/schema.sql
psql -U postgres -d cinema_db -f database/seed.sql
```

### 5. Серверді іске қосу
```bash
uvicorn src.main:app --reload
```

Сервер: http://localhost:8000  
Swagger UI: http://localhost:8000/docs

---

## 📡 API Эндпоинттары

| Метод | URL | Сипаттама |
|---|---|---|
| GET | `/api/movies` | Фильмдер тізімі |
| GET | `/api/movies?title=Дюна` | Атауы бойынша іздеу |
| GET | `/api/movies?genre=Триллер` | Жанр бойынша сүзгі |
| GET | `/api/movies/{id}` | Фильм детальдары |
| POST | `/api/movies` | Жаңа фильм қосу |
| PUT | `/api/movies/{id}` | Фильмді жаңарту |
| DELETE | `/api/movies/{id}` | Фильмді архивке жіберу |
| GET | `/api/sessions/{id}/seats` | Орындар бос/бронды күйі |
| POST | `/api/bookings` | Билет брондау |
| PUT | `/api/bookings/{id}` | Орынды ауыстыру |
| DELETE | `/api/bookings/{id}` | Броньды болдырмау |

---

## 🗄️ Дерекқор схемасы

6 байланысқан кесте:

```
movies   (1) ──── (N) sessions
halls    (1) ──── (N) seats
halls    (1) ──── (N) sessions
sessions (1) ──── (N) tickets
seats    (1) ──── (N) tickets
users    (1) ──── (N) tickets
```

Толық ER-диаграмма: [`docs/erd_diagram.pdf`](docs/erd_diagram.pdf)

---

## 👥 Команда

| Студент | GitHub | Рөл |
|---|---|---|
| 1-студент | @username1 | Backend, API |
| 2-студент | @username2 | Дерекқор, деплой |
| 3-студент | @username3 | Тестілеу |
