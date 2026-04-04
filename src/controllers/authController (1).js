// src/controllers/authController.js - Тіркелу және кіру логикасы

const db      = require('../../db/database');
const bcrypt  = require('bcryptjs');
const { validationResult } = require('express-validator');

// ============================================================
// POST /api/auth/register - Тіркелу
// ============================================================
function register(req, res) {
  // Валидация қателерін тексеру
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  const { name, email, password } = req.body;

  // Email бұрын тіркелген бе?
  const existing = db.prepare('SELECT id FROM users WHERE email = ?').get(email);
  if (existing) {
    return res.status(409).json({ error: 'Бұл email бұрын тіркелген' });
  }

  // Құпия сөзді хэштеу (10 - күрделілік деңгейі)
  const hashedPassword = bcrypt.hashSync(password, 10);

  // Дерекқорға жазу
  const result = db.prepare(`
    INSERT INTO users (name, email, password, role)
    VALUES (?, ?, ?, 'user')
  `).run(name, email, hashedPassword);

  res.status(201).json({
    message: 'Тіркелу сәтті!',
    userId: result.lastInsertRowid
  });
}

// ============================================================
// POST /api/auth/login - Жүйеге кіру
// ============================================================
function login(req, res) {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  const { email, password } = req.body;

  // Пайдаланушыны табу
  const user = db.prepare('SELECT * FROM users WHERE email = ?').get(email);
  if (!user) {
    return res.status(401).json({ error: 'Email немесе құпия сөз қате' });
  }

  // Құпия сөзді тексеру (хэш салыстыру)
  const isMatch = bcrypt.compareSync(password, user.password);
  if (!isMatch) {
    return res.status(401).json({ error: 'Email немесе құпия сөз қате' });
  }

  // Сессия сақтау
  req.session.userId = user.id;
  req.session.name   = user.name;
  req.session.role   = user.role;

  res.json({
    message: 'Кіру сәтті!',
    user: { id: user.id, name: user.name, email: user.email, role: user.role }
  });
}

// ============================================================
// POST /api/auth/logout - Шығу
// ============================================================
function logout(req, res) {
  req.session.destroy();
  res.json({ message: 'Жүйеден шықтыңыз' });
}

// ============================================================
// GET /api/auth/me - Ағымдағы пайдаланушы
// ============================================================
function getMe(req, res) {
  const user = db.prepare('SELECT id, name, email, role FROM users WHERE id = ?')
                 .get(req.session.userId);
  res.json(user);
}

module.exports = { register, login, logout, getMe };
