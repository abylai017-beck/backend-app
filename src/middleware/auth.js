// src/middleware/auth.js - Аутентификация тексеру

// Тек кірген пайдаланушыларға рұқсат беру
function requireLogin(req, res, next) {
  if (req.session && req.session.userId) {
    next(); // Кірген → жалғастыр
  } else {
    res.status(401).json({ error: 'Алдымен жүйеге кіріңіз' });
  }
}

// Тек админдерге рұқсат беру
function requireAdmin(req, res, next) {
  if (req.session && req.session.role === 'admin') {
    next(); // Админ → жалғастыр
  } else {
    res.status(403).json({ error: 'Тек админдерге рұқсат берілген' });
  }
}

module.exports = { requireLogin, requireAdmin };
