// src/controllers/sessionController.js - Сеанстармен жұмыс

const db = require('../../db/database');
const { validationResult } = require('express-validator');

// ============================================================
// GET /api/sessions - Барлық сеанстар (сүзгілеумен)
// ============================================================
function getAllSessions(req, res) {
  const { movie_id, date, hall } = req.query;

  let query = `
    SELECT s.*, m.title AS movie_title, m.genre, m.duration,
           COUNT(CASE WHEN seats.is_booked = 0 THEN 1 END) AS free_seats,
           COUNT(seats.id) AS total_seats_count
    FROM sessions s
    JOIN movies m ON m.id = s.movie_id
    LEFT JOIN seats ON seats.session_id = s.id
    WHERE 1=1
  `;
  const params = [];

  if (movie_id) { query += ' AND s.movie_id = ?'; params.push(movie_id); }
  if (date)     { query += ' AND DATE(s.date_time) = ?'; params.push(date); }
  if (hall)     { query += ' AND s.hall = ?'; params.push(hall); }

  query += ' GROUP BY s.id ORDER BY s.date_time';

  const sessions = db.prepare(query).all(...params);
  res.json({ count: sessions.length, sessions });
}

// ============================================================
// GET /api/sessions/:id/seats - Сеанстағы орындар картасы
// ============================================================
function getSeats(req, res) {
  const { id } = req.params;

  const session = db.prepare(`
    SELECT s.*, m.title AS movie_title
    FROM sessions s
    JOIN movies m ON m.id = s.movie_id
    WHERE s.id = ?
  `).get(id);

  if (!session) {
    return res.status(404).json({ error: 'Сеанс табылмады' });
  }

  const seats = db.prepare(`
    SELECT id, seat_number, is_booked
    FROM seats
    WHERE session_id = ?
    ORDER BY seat_number
  `).all(id);

  // Орындарды қатарлар бойынша топтастыру
  const seatMap = {};
  seats.forEach(seat => {
    const row = seat.seat_number[0]; // 'A', 'B', 'C'...
    if (!seatMap[row]) seatMap[row] = [];
    seatMap[row].push(seat);
  });

  const freeCount   = seats.filter(s => s.is_booked === 0).length;
  const bookedCount = seats.filter(s => s.is_booked === 1).length;

  res.json({
    session,
    stats: { total: seats.length, free: freeCount, booked: bookedCount },
    seatMap
  });
}

// ============================================================
// POST /api/sessions - Жаңа сеанс қосу (тек админ)
// ============================================================
function createSession(req, res) {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  const { movie_id, hall, date_time, price, total_seats } = req.body;

  // Фильм бар ма?
  const movie = db.prepare('SELECT id FROM movies WHERE id = ?').get(movie_id);
  if (!movie) {
    return res.status(404).json({ error: 'Фильм табылмады' });
  }

  const result = db.prepare(`
    INSERT INTO sessions (movie_id, hall, date_time, price, total_seats)
    VALUES (?, ?, ?, ?, ?)
  `).run(movie_id, hall, date_time, price, total_seats || 30);

  const sessionId = result.lastInsertRowid;

  // Орындарды автоматты жасау
  const rows = ['A','B','C','D','E'];
  const cols = total_seats <= 30 ? [1,2,3,4,5,6] : [1,2,3,4,5,6,7,8,9,10];

  const insertSeat = db.prepare(
    'INSERT INTO seats (session_id, seat_number) VALUES (?, ?)'
  );
  rows.forEach(row => cols.forEach(col => insertSeat.run(sessionId, `${row}${col}`)));

  res.status(201).json({
    message: 'Сеанс сәтті жасалды!',
    sessionId,
    seatsCreated: rows.length * cols.length
  });
}

// ============================================================
// DELETE /api/sessions/:id - Сеансты өшіру (тек админ)
// ============================================================
function deleteSession(req, res) {
  const { id } = req.params;

  const session = db.prepare('SELECT * FROM sessions WHERE id = ?').get(id);
  if (!session) {
    return res.status(404).json({ error: 'Сеанс табылмады' });
  }

  db.prepare('DELETE FROM sessions WHERE id = ?').run(id);
  res.json({ message: 'Сеанс өшірілді' });
}

module.exports = { getAllSessions, getSeats, createSession, deleteSession };
