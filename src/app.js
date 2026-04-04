// src/app.js - Негізгі серверлік файл

const express       = require('express');
const session       = require('express-session');
const cookieParser  = require('cookie-parser');
const path          = require('path');

const routes = require('./routes/index');

const app  = express();
const PORT = process.env.PORT || 3000;

// ============================================================
// MIDDLEWARE (сұрауды өңдеу тізбегі)
// ============================================================

// JSON деректерін оқу
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// Статикалық файлдар (HTML, CSS, JS)
app.use(express.static(path.join(__dirname, '..', 'public')));

// Сессия баптауы
app.use(session({
  secret:            'cinema-secret-key-2025', // Нақты жобада .env-тен оқу керек!
  resave:            false,
  saveUninitialized: false,
  cookie: {
    maxAge: 24 * 60 * 60 * 1000 // 24 сағат
  }
}));

// ============================================================
// API МАРШРУТТАРЫ
// ============================================================
app.use('/api', routes);

// ============================================================
// ФРОНТЕНД - HTML беттерді қайтару
// ============================================================
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'public', 'index.html'));
});

// 404 қате өңдеу
app.use((req, res) => {
  res.status(404).json({ error: 'Маршрут табылмады' });
});

// Жалпы қате өңдеу
app.use((err, req, res, next) => {
  console.error('Қате:', err.message);
  res.status(500).json({ error: 'Сервер қатесі орын алды' });
});

// ============================================================
// СЕРВЕРДІ ІСКЕ ҚОСУ
// ============================================================
app.listen(PORT, () => {
  console.log('');
  console.log('🎬 Кинотеатр жүйесі іске қосылды!');
  console.log(`🌐 Адрес: http://localhost:${PORT}`);
  console.log('');
  console.log('📋 API Эндпоинттер:');
  console.log('   POST /api/auth/register  - Тіркелу');
  console.log('   POST /api/auth/login     - Кіру');
  console.log('   GET  /api/movies         - Фильмдер тізімі');
  console.log('   GET  /api/sessions       - Сеанстар тізімі');
  console.log('   POST /api/tickets/book   - Билет сатып алу');
  console.log('');
});

module.exports = app;
