// db/seed.js - Тест деректерімен толтыру

const db = require('./database');
const bcrypt = require('bcryptjs');

console.log('🌱 Тест деректерін қосу басталды...');

// ============================================================
// 1. ПАЙДАЛАНУШЫЛАР қосу
// ============================================================
const adminPassword = bcrypt.hashSync('admin123', 10);
const userPassword  = bcrypt.hashSync('user123', 10);

const insertUser = db.prepare(`
  INSERT OR IGNORE INTO users (name, email, password, role)
  VALUES (?, ?, ?, ?)
`);

insertUser.run('Админ',       'admin@cinema.kz', adminPassword, 'admin');
insertUser.run('Асель Нурова','asel@mail.kz',     userPassword,  'user');
insertUser.run('Берік Алиев', 'berik@mail.kz',    userPassword,  'user');

// ============================================================
// 2. ФИЛЬМДЕР қосу
// ============================================================
const insertMovie = db.prepare(`
  INSERT OR IGNORE INTO movies (title, description, genre, duration, poster_url)
  VALUES (?, ?, ?, ?, ?)
`);

const movies = [
  ['Гладиатор 2',    'Рим империясының жаңа батыры туралы эпикалық фильм',   'Боевик',    148, '/images/gladiator2.jpg'],
  ['Дюна: 3 бөлім',  'Пол Атрейдестің ғарыш саяхаты жалғасады',              'Ғылыми фантастика', 166, '/images/dune3.jpg'],
  ['Мастер',         'Абылай ханның өмірі туралы қазақ тарихи фильмі',        'Тарихи',   134, '/images/master.jpg'],
  ['Смешарики',      'Балаларға арналған мультфильм',                         'Мультфильм', 90, '/images/smeshariki.jpg'],
];

movies.forEach(m => insertMovie.run(...m));

// ============================================================
// 3. СЕАНСТАР қосу
// ============================================================
const insertSession = db.prepare(`
  INSERT OR IGNORE INTO sessions (movie_id, hall, date_time, price, total_seats)
  VALUES (?, ?, ?, ?, ?)
`);

const sessionData = [
  [1, 'Зал 1', '2025-06-15 10:00', 1500, 30],
  [1, 'Зал 2', '2025-06-15 14:00', 1800, 30],
  [2, 'Зал 1', '2025-06-15 18:00', 2000, 30],
  [3, 'Зал 3', '2025-06-16 12:00', 1200, 30],
  [4, 'Зал 2', '2025-06-16 15:00', 800,  30],
];

sessionData.forEach(s => insertSession.run(...s));

// ============================================================
// 4. ОРЫНДАР жасау (әр сеанс үшін 30 орын: A1-E6)
// ============================================================
const insertSeat = db.prepare(`
  INSERT OR IGNORE INTO seats (session_id, seat_number, is_booked)
  VALUES (?, ?, 0)
`);

// Барлық сеанстар үшін орын жасаймыз
const allSessions = db.prepare('SELECT id FROM sessions').all();
const rows    = ['A', 'B', 'C', 'D', 'E'];
const cols    = [1, 2, 3, 4, 5, 6];

allSessions.forEach(session => {
  rows.forEach(row => {
    cols.forEach(col => {
      insertSeat.run(session.id, `${row}${col}`);
    });
  });
});

console.log('✅ Тест деректері сәтті қосылды!');
console.log('');
console.log('📧 Кіру мәліметтері:');
console.log('   Админ:      admin@cinema.kz / admin123');
console.log('   Пайдаланушы: asel@mail.kz  / user123');
