// src/controllers/movieController.js - Фильмдермен жұмыс

const db = require('../../db/database');
const { validationResult } = require('express-validator');

// ============================================================
// GET /api/movies - Барлық фильмдер (іздеу + сүзгілеу)
// ============================================================
function getAllMovies(req, res) {
  const { search, genre } = req.query;

  let query  = 'SELECT * FROM movies WHERE 1=1';
  const params = [];

  // Іздеу - атауы бойынша
  if (search) {
    query += ' AND title LIKE ?';
    params.push(`%${search}%`);
  }

  // Сүзгілеу - жанры бойынша
  if (genre) {
    query += ' AND genre = ?';
    params.push(genre);
  }

  query += ' ORDER BY created_at DESC';

  const movies = db.prepare(query).all(...params);
  res.json({ count: movies.length, movies });
}

// ============================================================
// GET /api/movies/:id - Бір фильм (сеанстарымен бірге)
// ============================================================
function getMovieById(req, res) {
  const { id } = req.params;

  const movie = db.prepare('SELECT * FROM movies WHERE id = ?').get(id);
  if (!movie) {
    return res.status(404).json({ error: 'Фильм табылмады' });
  }

  // JOIN: фильммен бірге сеанстарды да қайтар
  const sessions = db.prepare(`
    SELECT s.id, s.hall, s.date_time, s.price, s.total_seats,
           COUNT(CASE WHEN seats.is_booked = 0 THEN 1 END) AS free_seats
    FROM sessions s
    LEFT JOIN seats ON seats.session_id = s.id
    WHERE s.movie_id = ?
    GROUP BY s.id
    ORDER BY s.date_time
  `).all(id);

  res.json({ ...movie, sessions });
}

// ============================================================
// POST /api/movies - Жаңа фильм қосу (тек админ)
// ============================================================
function createMovie(req, res) {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  const { title, description, genre, duration, poster_url } = req.body;

  const result = db.prepare(`
    INSERT INTO movies (title, description, genre, duration, poster_url)
    VALUES (?, ?, ?, ?, ?)
  `).run(title, description || '', genre, duration, poster_url || '');

  const newMovie = db.prepare('SELECT * FROM movies WHERE id = ?').get(result.lastInsertRowid);
  res.status(201).json({ message: 'Фильм сәтті қосылды!', movie: newMovie });
}

// ============================================================
// PUT /api/movies/:id - Фильмді жаңарту (тек админ)
// ============================================================
function updateMovie(req, res) {
  const { id } = req.params;

  const movie = db.prepare('SELECT * FROM movies WHERE id = ?').get(id);
  if (!movie) {
    return res.status(404).json({ error: 'Фильм табылмады' });
  }

  const { title, description, genre, duration, poster_url } = req.body;

  db.prepare(`
    UPDATE movies
    SET title=?, description=?, genre=?, duration=?, poster_url=?
    WHERE id=?
  `).run(
    title       || movie.title,
    description || movie.description,
    genre       || movie.genre,
    duration    || movie.duration,
    poster_url  || movie.poster_url,
    id
  );

  const updated = db.prepare('SELECT * FROM movies WHERE id = ?').get(id);
  res.json({ message: 'Фильм жаңартылды', movie: updated });
}

// ============================================================
// DELETE /api/movies/:id - Фильмді өшіру (тек админ)
// ============================================================
function deleteMovie(req, res) {
  const { id } = req.params;

  const movie = db.prepare('SELECT * FROM movies WHERE id = ?').get(id);
  if (!movie) {
    return res.status(404).json({ error: 'Фильм табылмады' });
  }

  db.prepare('DELETE FROM movies WHERE id = ?').run(id);
  res.json({ message: `"${movie.title}" фильмі өшірілді` });
}

// ============================================================
// GET /api/movies/genres - Барлық жанрлар
// ============================================================
function getGenres(req, res) {
  const genres = db.prepare('SELECT DISTINCT genre FROM movies ORDER BY genre').all();
  res.json(genres.map(g => g.genre));
}

module.exports = { getAllMovies, getMovieById, createMovie, updateMovie, deleteMovie, getGenres };
