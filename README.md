[README.md](https://github.com/user-attachments/files/26479766/README.md)
# 🎬 Cinema KZ — Кинотеатр билеттерін сату жүйесі

## Жоба туралы
Node.js, Express.js және SQLite негізінде жасалған кинотеатр билеттерін онлайн сату веб-қосымшасы.

## 🛠 Технологиялар
| Технология | Мақсаты |
|---|---|
| Node.js | Серверлік орта |
| Express.js | Веб-фреймворк |
| better-sqlite3 | Дерекқор (SQLite) |
| bcryptjs | Құпия сөзді хэштеу |
| express-session | Сессиялар |
| express-validator | Валидация |


### 📊 ERD диаграмма:

![ERD](./docs/erd.png)


## 🚀 API Documentation

Толық API құжаттамасы:

👉 [API_DOCS.md](./API_DOCS.md)



## 📁 Жоба құрылымы
```
cinema-app/
├── src/
│   ├── app.js                  # Негізгі сервер
│   ├── controllers/
│   │   ├── authController.js   # Тіркелу/кіру логикасы
│   │   ├── movieController.js  # Фильмдермен жұмыс
│   │   ├── sessionController.js# Сеанстармен жұмыс
│   │   └── ticketController.js # Билет сату логикасы
│   ├── middleware/
│   │   └── auth.js             # Аутентификация тексеру
│   └── routes/
│       └── index.js            # Барлық маршруттар
├── db/
│   ├── database.js             # Дерекқор қосылымы
│   └── seed.js                 # Тест деректері
├── public/
│   └── index.html              # Фронтенд
├── .gitignore
├── package.json
└── README.md
```

## 🗄 Дерекқор схемасы (ERD)

```
users (пайдаланушылар)
  id, name, email, password, role, created_at
       ↓
tickets (билеттер)
  id, user_id, seat_id, session_id, total_price, status, created_at

movies (фильмдер)          sessions (сеанстар)        seats (орындар)
  id, title, genre    →→→   id, movie_id, hall,   →→→  id, session_id,
  duration, desc            date_time, price             seat_number, is_booked
```

**Байланыстар:**
- `users` → `tickets` : One-to-Many (бір пайдаланушы көп билет)
- `movies` → `sessions` : One-to-Many (бір фильм көп сеанс)
- `sessions` → `seats` : One-to-Many (бір сеансда көп орын)
- `seats` → `tickets` : One-to-One (бір орынға бір билет)

## 🚀 Іске қосу нұсқаулығы

```bash
# 1. Жобаны клондау
git clone <repo-url>
cd cinema-app

# 2. Тәуелділіктерді орнату
npm install

# 3. Тест деректерін қосу
npm run seed

# 4. Серверді іске қосу
npm start
# немесе автоматты жаңарту үшін:
npm run dev

# 5. Браузерде ашу
# http://localhost:3000
```

## 📧 Демо есептер
| Рөл | Email | Құпия сөз |
|---|---|---|
| Админ | admin@cinema.kz | admin123 |
| Пайдаланушы | asel@mail.kz | user123 |

## 🔌 API Эндпоинттер

### Аутентификация
| Метод | URL | Сипаттама |
|---|---|---|
| POST | /api/auth/register | Тіркелу |
| POST | /api/auth/login | Кіру |
| POST | /api/auth/logout | Шығу |
| GET  | /api/auth/me | Ағымдағы пайдаланушы |

### Фильмдер
| Метод | URL | Сипаттама |
|---|---|---|
| GET    | /api/movies | Барлық фильмдер (?search=&genre=) |
| GET    | /api/movies/:id | Бір фильм + сеанстары |
| GET    | /api/movies/genres | Жанрлар тізімі |
| POST   | /api/movies | Жаңа фильм (тек админ) |
| PUT    | /api/movies/:id | Фильмді жаңарту (тек админ) |
| DELETE | /api/movies/:id | Фильмді өшіру (тек админ) |

### Сеанстар
| Метод | URL | Сипаттама |
|---|---|---|
| GET    | /api/sessions | Барлық сеанстар (?movie_id=&date=) |
| GET    | /api/sessions/:id/seats | Орындар картасы |
| POST   | /api/sessions | Жаңа сеанс (тек админ) |
| DELETE | /api/sessions/:id | Сеансты өшіру (тек админ) |

### Билеттер
| Метод | URL | Сипаттама |
|---|---|---|
| POST   | /api/tickets/book | Орын брондау |
| GET    | /api/tickets/my | Менің билеттерім |
| DELETE | /api/tickets/:id/cancel | Болдырмау |
| GET    | /api/tickets/all | Барлық билеттер (тек админ) |

## ✅ Функционалдылық
- [x] Аутентификация (тіркелу, кіру, шығу)
- [x] Дерекқор (5 байланысқан кесте)
- [x] CRUD операциялары (фильмдер, сеанстар, билеттер)
- [x] REST API (GET, POST, PUT, DELETE)
- [x] Валидация (email, міндетті өрістер)
- [x] Іздеу және сүзгілеу (атауы, жанры, күні)
- [x] Орындарды интерактивті таңдау
- [x] Транзакциялар (деректер бүтіндігі)
- [x] Фронтенд (толық UI)

## 🌐 Деплой (Render.com)
1. GitHub-қа push жасаңыз
2. render.com-да тіркеліңіз
3. "New Web Service" → репозиторийді таңдаңыз
4. Build command: `npm install && npm run seed`
5. Start command: `npm start`
