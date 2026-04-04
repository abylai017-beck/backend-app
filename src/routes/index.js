// src/routes/index.js - Барлық маршруттар

const express = require('express');
const router  = express.Router();
const { body } = require('express-validator');

const authCtrl    = require('../controllers/authController');
const movieCtrl   = require('../controllers/movieController');
const sessionCtrl = require('../controllers/sessionController');
const ticketCtrl  = require('../controllers/ticketController');
const { requireLogin, requireAdmin } = require('../middleware/auth');

// ============================================================
// AUTH МАРШРУТТАРЫ
// ============================================================
router.post('/auth/register',
  [
    body('name').notEmpty().withMessage('Аты міндетті'),
    body('email').isEmail().withMessage('Email форматы дұрыс емес'),
    body('password').isLength({ min: 6 }).withMessage('Құпия сөз кемінде 6 символ'),
  ],
  authCtrl.register
);

router.post('/auth/login',
  [
    body('email').isEmail().withMessage('Email форматы дұрыс емес'),
    body('password').notEmpty().withMessage('Құпия сөз міндетті'),
  ],
  authCtrl.login
);

router.post('/auth/logout', authCtrl.logout);
router.get('/auth/me', requireLogin, authCtrl.getMe);

// ============================================================
// ФИЛЬМДЕР МАРШРУТТАРЫ
// ============================================================
router.get('/movies/genres', movieCtrl.getGenres);      // Жанрлар тізімі
router.get('/movies',        movieCtrl.getAllMovies);    // Барлық фильмдер
router.get('/movies/:id',    movieCtrl.getMovieById);   // Бір фильм

// Тек админ жасай алады
router.post('/movies',
  requireLogin, requireAdmin,
  [
    body('title').notEmpty().withMessage('Атауы міндетті'),
    body('genre').notEmpty().withMessage('Жанры міндетті'),
    body('duration').isInt({ min: 1 }).withMessage('Ұзақтығы дұрыс емес'),
  ],
  movieCtrl.createMovie
);
router.put('/movies/:id',    requireLogin, requireAdmin, movieCtrl.updateMovie);
router.delete('/movies/:id', requireLogin, requireAdmin, movieCtrl.deleteMovie);

// ============================================================
// СЕАНСТАР МАРШРУТТАРЫ
// ============================================================
router.get('/sessions',           sessionCtrl.getAllSessions);
router.get('/sessions/:id/seats', sessionCtrl.getSeats);

router.post('/sessions',
  requireLogin, requireAdmin,
  [
    body('movie_id').isInt().withMessage('movie_id міндетті'),
    body('hall').notEmpty().withMessage('Зал аты міндетті'),
    body('date_time').notEmpty().withMessage('Уақыт міндетті'),
    body('price').isFloat({ min: 0 }).withMessage('Баға дұрыс емес'),
  ],
  sessionCtrl.createSession
);
router.delete('/sessions/:id', requireLogin, requireAdmin, sessionCtrl.deleteSession);

// ============================================================
// БИЛЕТТЕР МАРШРУТТАРЫ
// ============================================================
router.post('/tickets/book',       requireLogin, ticketCtrl.bookTicket);
router.get('/tickets/my',          requireLogin, ticketCtrl.getMyTickets);
router.delete('/tickets/:id/cancel', requireLogin, ticketCtrl.cancelTicket);
router.get('/tickets/all',         requireLogin, requireAdmin, ticketCtrl.getAllTickets);

module.exports = router;
