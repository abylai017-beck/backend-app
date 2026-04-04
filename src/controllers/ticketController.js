// src/controllers/ticketController.js - Билет сату логикасы

const db = require('../../db/database');

// ============================================================
// POST /api/tickets/book - Орын брондау (билет сатып алу)
// ============================================================
function bookTicket(req, res) {
  const { session_id, seat_numbers } = req.body;
  const userId = req.session.userId;

  // Валидация
  if (!session_id || !seat_numbers || !Array.isArray(seat_numbers) || seat_numbers.length === 0) {
    return res.status(400).json({ error: 'session_id және seat_numbers массиві міндетті' });
  }

  // Сеансты тексеру
  const session = db.prepare('SELECT * FROM sessions WHERE id = ?').get(session_id);
  if (!session) {
    return res.status(404).json({ error: 'Сеанс табылмады' });
  }

  // ТРАНЗАКЦИЯ - барлығы сәтті болмаса, ештеңе сақталмайды
  const bookTransaction = db.transaction(() => {
    const bookedSeats = [];

    for (const seatNumber of seat_numbers) {
      // Орынды табу
      const seat = db.prepare(`
        SELECT * FROM seats
        WHERE session_id = ? AND seat_number = ?
      `).get(session_id, seatNumber);

      if (!seat) {
        throw new Error(`Орын "${seatNumber}" табылмады`);
      }

      if (seat.is_booked === 1) {
        throw new Error(`"${seatNumber}" орны бос емес`);
      }

      // Орынды брондау
      db.prepare('UPDATE seats SET is_booked = 1 WHERE id = ?').run(seat.id);

      // Билет жасау
      const ticketResult = db.prepare(`
        INSERT INTO tickets (user_id, seat_id, session_id, total_price)
        VALUES (?, ?, ?, ?)
      `).run(userId, seat.id, session_id, session.price);

      bookedSeats.push({
        ticketId:   ticketResult.lastInsertRowid,
        seatNumber: seatNumber,
        price:      session.price
      });
    }

    return bookedSeats;
  });

  try {
    const result = bookTransaction();
    const totalPrice = result.length * session.price;

    res.status(201).json({
      message: 'Билет(тер) сәтті сатып алынды! 🎬',
      tickets: result,
      totalPrice,
      currency: 'тг'
    });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
}

// ============================================================
// GET /api/tickets/my - Менің билеттерім
// ============================================================
function getMyTickets(req, res) {
  const userId = req.session.userId;

  // JOIN арқылы барлық қажетті деректерді бір сұраумен алу
  const tickets = db.prepare(`
    SELECT
      t.id          AS ticket_id,
      t.total_price,
      t.status,
      t.created_at,
      seats.seat_number,
      s.hall,
      s.date_time,
      s.price       AS seat_price,
      m.title       AS movie_title,
      m.genre,
      m.duration
    FROM tickets t
    JOIN seats   ON seats.id   = t.seat_id
    JOIN sessions s ON s.id    = t.session_id
    JOIN movies m ON m.id      = s.movie_id
    WHERE t.user_id = ?
    ORDER BY t.created_at DESC
  `).all(userId);

  res.json({ count: tickets.length, tickets });
}

// ============================================================
// DELETE /api/tickets/:id/cancel - Билетті болдырмау
// ============================================================
function cancelTicket(req, res) {
  const { id }  = req.params;
  const userId  = req.session.userId;

  const ticket = db.prepare('SELECT * FROM tickets WHERE id = ? AND user_id = ?').get(id, userId);
  if (!ticket) {
    return res.status(404).json({ error: 'Билет табылмады' });
  }

  if (ticket.status === 'cancelled') {
    return res.status(400).json({ error: 'Билет бұрын болдырмаған' });
  }

  // Транзакция: билетті болдырмау + орынды босату
  const cancelTransaction = db.transaction(() => {
    db.prepare("UPDATE tickets SET status = 'cancelled' WHERE id = ?").run(id);
    db.prepare('UPDATE seats SET is_booked = 0 WHERE id = ?').run(ticket.seat_id);
  });

  cancelTransaction();
  res.json({ message: 'Билет болдырмаланды, орын босатылды' });
}

// ============================================================
// GET /api/tickets/all - Барлық билеттер (тек админ)
// ============================================================
function getAllTickets(req, res) {
  const tickets = db.prepare(`
    SELECT
      t.id, t.total_price, t.status, t.created_at,
      u.name AS user_name, u.email,
      seats.seat_number,
      s.hall, s.date_time,
      m.title AS movie_title
    FROM tickets t
    JOIN users u   ON u.id   = t.user_id
    JOIN seats     ON seats.id = t.seat_id
    JOIN sessions s ON s.id  = t.session_id
    JOIN movies m  ON m.id   = s.movie_id
    ORDER BY t.created_at DESC
  `).all();

  res.json({ count: tickets.length, tickets });
}

module.exports = { bookTicket, getMyTickets, cancelTicket, getAllTickets };
