const API = 'http://127.0.0.1:8000';
let token    = localStorage.getItem('cf_token') || '';
let username = localStorage.getItem('cf_user')  || '';
let userRole = localStorage.getItem('cf_role')  || 'user';
let currentSession = null;
let selectedSeat   = null;
let searchTimer    = null;

window.onload = () => {
  if (token) { showApp(); loadMovies(); }
  else        { showAuth(); }
};

function showAuth() {
  document.getElementById('auth-section').classList.remove('hidden');
  document.getElementById('main-section').classList.add('hidden');
}
function showApp() {
  document.getElementById('auth-section').classList.add('hidden');
  document.getElementById('main-section').classList.remove('hidden');
  document.getElementById('nav-username').textContent = '👤 ' + username;
  if (userRole === 'admin') {
    document.querySelectorAll('.admin-only').forEach(el => el.classList.remove('hidden'));
  }
}
function showLogin() {
  document.getElementById('login-box').classList.remove('hidden');
  document.getElementById('reg-box').classList.add('hidden');
}
function showReg() {
  document.getElementById('login-box').classList.add('hidden');
  document.getElementById('reg-box').classList.remove('hidden');
}

async function doLogin() {
  const u = document.getElementById('l-user').value.trim();
  const p = document.getElementById('l-pass').value;
  if (!u || !p) { toast('Заполните все поля', 'error'); return; }
  const btn = document.getElementById('btn-login');
  btn.disabled = true; btn.textContent = 'Вход...';
  try {
    const res = await api('POST', '/auth/login', { username: u, password: p });
    saveAuth(res);
    showApp(); loadMovies();
    toast('Добро пожаловать, ' + res.username + '!');
  } catch(e) { toast(e.message, 'error'); }
  finally { btn.disabled = false; btn.textContent = 'Войти'; }
}

async function doRegister() {
  const u = document.getElementById('r-user').value.trim();
  const e = document.getElementById('r-email').value.trim();
  const p = document.getElementById('r-pass').value;
  if (!u || !e || !p) { toast('Заполните все поля', 'error'); return; }
  if (p.length < 6)   { toast('Пароль минимум 6 символов', 'error'); return; }
  try {
    const res = await api('POST', '/auth/register', { username: u, email: e, password: p });
    saveAuth(res);
    showApp(); loadMovies();
    toast('Аккаунт создан!');
  } catch(e) { toast(e.message, 'error'); }
}

function saveAuth(res) {
  token = res.token; username = res.username; userRole = res.role;
  localStorage.setItem('cf_token', token);
  localStorage.setItem('cf_user',  username);
  localStorage.setItem('cf_role',  userRole);
}

function doLogout() {
  token = username = userRole = '';
  localStorage.removeItem('cf_token');
  localStorage.removeItem('cf_user');
  localStorage.removeItem('cf_role');
  showAuth(); showLogin();
  toast('Вы вышли из аккаунта', 'info');
}

function showPage(page, btn) {
  document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
  document.querySelectorAll('.ntab').forEach(b => b.classList.remove('active'));
  document.getElementById('page-' + page).classList.remove('hidden');
  btn.classList.add('active');

  if (page === 'sessions')  loadSessions();
  if (page === 'mytickets') loadMyTickets();
  if (page === 'admin')     loadAdminData();
}

async function loadMovies(search = '') {
  const grid = document.getElementById('movies-grid');
  grid.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Загрузка...</p></div>';
  try {
    let url = '/movies';
    if (search) url += '?search=' + encodeURIComponent(search);
    const movies = await api('GET', url);
    grid.innerHTML = '';
    if (!movies.length) {
      grid.innerHTML = '<div class="empty-state"><div class="empty-icon">🎬</div><p>Фильмы не найдены</p></div>';
      return;
    }
    movies.forEach((m, i) => {
      const card = document.createElement('div');
      card.className = 'movie-card';
      card.style.animationDelay = i * 50 + 'ms';
      card.innerHTML = `
        ${m.poster_url
          ? `<img class="movie-poster" src="${esc(m.poster_url)}" alt="${esc(m.title)}" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">`
          : ''}
        <div class="movie-poster-placeholder" ${m.poster_url ? 'style="display:none"' : ''}>🎬</div>
        <div class="movie-info">
          <div class="movie-title">${esc(m.title)}</div>
          <div class="movie-genre">${esc(m.genre || 'Фильм')}</div>
          <div class="movie-meta">
            <span class="movie-rating">★ ${m.rating}</span>
            <span class="movie-dur">${m.duration} мин</span>
          </div>
        </div>
        <button class="btn-sessions" onclick="goToSessions(${m.id})">Купить билет</button>
      `;
      grid.appendChild(card);
    });
  } catch(e) { grid.innerHTML = '<div class="empty-state"><div class="empty-icon">⚠️</div><p>Ошибка загрузки</p></div>'; }
}

function searchMovies() {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    loadMovies(document.getElementById('movie-search').value.trim());
  }, 350);
}

function goToSessions(movieId) {
  document.querySelectorAll('.ntab').forEach(b => b.classList.remove('active'));
  document.querySelector('[data-page="sessions"]').classList.add('active');
  document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
  document.getElementById('page-sessions').classList.remove('hidden');
  loadSessions(movieId);
}

async function loadSessions(movieId = null) {
  const list = document.getElementById('sessions-list');
  list.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Загрузка...</p></div>';
  try {
    let url = '/sessions';
    if (movieId) url += '?movie_id=' + movieId;
    const sessions = await api('GET', url);
    list.innerHTML = '';
    if (!sessions.length) {
      list.innerHTML = '<div class="empty-state"><div class="empty-icon">🕐</div><p>Сеансов нет</p></div>';
      return;
    }
    sessions.forEach((s, i) => {
      const dt = new Date(s.start_time);
      const timeStr = dt.toLocaleTimeString('ru', { hour: '2-digit', minute: '2-digit' });
      const dateStr = dt.toLocaleDateString('ru', { day: 'numeric', month: 'long' });
      const row = document.createElement('div');
      row.className = 'session-row';
      row.style.animationDelay = i * 40 + 'ms';
      row.innerHTML = `
        ${s.poster_url
          ? `<img class="session-poster" src="${esc(s.poster_url)}" alt="${esc(s.movie_title)}">`
          : '<div class="session-poster" style="background:var(--surface2);display:flex;align-items:center;justify-content:center;font-size:20px">🎬</div>'}
        <div class="session-info">
          <div class="session-movie">${esc(s.movie_title)}</div>
          <div class="session-meta">
            <span class="schip">📅 ${dateStr}</span>
            <span class="schip">🏛️ ${esc(s.hall_name)}</span>
            <span class="schip">⏱️ ${s.duration} мин</span>
            ${s.genre ? `<span class="schip">${esc(s.genre)}</span>` : ''}
          </div>
        </div>
        <div>
          <div class="session-time">${timeStr}</div>
          <div class="session-price">${s.price.toLocaleString()} тг</div>
        </div>
        <button class="btn-buy" onclick="openSeatModal(${JSON.stringify(s).replace(/"/g,'&quot;')})">
          Выбрать место
        </button>
      `;
      list.appendChild(row);
    });
  } catch(e) { list.innerHTML = '<div class="empty-state"><div class="empty-icon">⚠️</div><p>Ошибка загрузки</p></div>'; }
}

async function openSeatModal(session) {
  currentSession = session;
  selectedSeat   = null;

  const dt      = new Date(session.start_time);
  const timeStr = dt.toLocaleTimeString('ru', { hour: '2-digit', minute: '2-digit' });
  const dateStr = dt.toLocaleDateString('ru', { day: 'numeric', month: 'long' });

  document.getElementById('seat-modal-title').textContent = session.movie_title;
  document.getElementById('seat-modal-sub').textContent   = `${dateStr} в ${timeStr} · ${session.hall_name} · ${session.price.toLocaleString()} тг`;
  document.getElementById('seat-summary').textContent     = 'Выберите место';
  document.getElementById('seat-summary').className       = 'seat-summary';
  document.getElementById('btn-book').disabled            = true;

  document.getElementById('seat-modal').classList.remove('hidden');
  await renderSeats(session.id);
}

function closeSeatModal() {
  document.getElementById('seat-modal').classList.add('hidden');
  currentSession = null; selectedSeat = null;
}

async function renderSeats(sessionId) {
  const map = document.getElementById('seat-map');
  map.innerHTML = '<div class="loading-state"><div class="spinner"></div></div>';
  try {
    const data = await api('GET', '/sessions/' + sessionId + '/seats');
    map.innerHTML = '';
    const rows = {};
    data.seats.forEach(s => {
      if (!rows[s.row]) rows[s.row] = [];
      rows[s.row].push(s);
    });

    Object.keys(rows).sort((a,b) => a-b).forEach(rowNum => {
      const rowWrap = document.createElement('div');
      rowWrap.className = 'seat-row-wrap';
      const lbl = document.createElement('div');
      lbl.className = 'row-num'; lbl.textContent = rowNum;
      rowWrap.appendChild(lbl);

      rows[rowNum].forEach(seat => {
        const el = document.createElement('div');
        el.className = 'seat' + (seat.status === 'booked' ? ' booked' : '');
        el.title = `Ряд ${seat.row}, место ${seat.col}`;
        el.textContent = seat.col;
        if (seat.status !== 'booked') {
          el.onclick = () => selectSeat(seat.row, seat.col, el);
        }
        rowWrap.appendChild(el);
      });
      map.appendChild(rowWrap);
    });
  } catch(e) { map.innerHTML = '<p style="color:var(--red);text-align:center">Ошибка загрузки мест</p>'; }
}

function selectSeat(row, col, el) {
  document.querySelectorAll('.seat.selected').forEach(s => s.classList.remove('selected'));
  selectedSeat = { row, col };
  el.classList.add('selected');

  const price = currentSession.price.toLocaleString();
  const summary = document.getElementById('seat-summary');
  summary.innerHTML = `<strong>Ряд ${row}, место ${col}</strong> · <span style="color:var(--accent)">${price} тг</span>`;
  summary.className = 'seat-summary has-seat';
  document.getElementById('btn-book').disabled = false;
}

async function confirmBooking() {
  if (!selectedSeat || !currentSession) return;
  const btn = document.getElementById('btn-book');
  btn.disabled = true; btn.textContent = 'Покупка...';
  try {
    await api('POST', '/tickets', {
      session_id: currentSession.id,
      seat_row:   selectedSeat.row,
      seat_col:   selectedSeat.col
    });
    closeSeatModal();
    toast('🎟️ Билет куплен! Приятного просмотра!', 'success');
  } catch(e) {
    toast(e.message, 'error');
    await renderSeats(currentSession.id);
    selectedSeat = null;
    document.getElementById('btn-book').disabled = true;
    document.getElementById('seat-summary').textContent = 'Выберите другое место';
    document.getElementById('seat-summary').className = 'seat-summary';
  } finally {
    btn.textContent = 'Купить билет';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('seat-modal').addEventListener('click', function(e) {
    if (e.target === this) closeSeatModal();
  });
});

async function loadMyTickets() {
  const list = document.getElementById('my-tickets-list');
  list.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Загрузка...</p></div>';
  try {
    const tickets = await api('GET', '/tickets/my');
    list.innerHTML = '';
    if (!tickets.length) {
      list.innerHTML = '<div class="empty-state"><div class="empty-icon">🎟️</div><p>Билетов нет</p><span style="font-size:13px;color:var(--muted)">Купите первый билет!</span></div>';
      return;
    }
    tickets.forEach((t, i) => {
      const dt = new Date(t.start_time);
      const card = document.createElement('div');
      card.className = 'ticket-card';
      card.style.animationDelay = i * 40 + 'ms';
      card.innerHTML = `
        <div class="ticket-movie">${esc(t.movie_title)}</div>
        <div class="ticket-info">
          <div class="ticket-row"><span>Дата</span><span>${dt.toLocaleDateString('ru', {day:'numeric',month:'long',year:'numeric'})}</span></div>
          <div class="ticket-row"><span>Время</span><span>${dt.toLocaleTimeString('ru',{hour:'2-digit',minute:'2-digit'})}</span></div>
          <div class="ticket-row"><span>Зал</span><span>${esc(t.hall_name)}</span></div>
          <div class="ticket-row"><span>Цена</span><span style="color:var(--accent)">${t.price.toLocaleString()} тг</span></div>
        </div>
        <div class="ticket-seat">Ряд ${t.seat_row} · Место ${t.seat_col}</div>
        <button class="btn-cancel-ticket" onclick="cancelTicket(${t.id}, this)">Отменить билет</button>
      `;
      list.appendChild(card);
    });
  } catch(e) { list.innerHTML = '<div class="empty-state"><div class="empty-icon">⚠️</div><p>Ошибка загрузки</p></div>'; }
}

async function cancelTicket(id, btn) {
  if (!confirm('Отменить билет?')) return;
  btn.disabled = true; btn.textContent = 'Отмена...';
  try {
    await api('DELETE', '/tickets/' + id);
    toast('Билет отменён', 'info');
    loadMyTickets();
  } catch(e) { toast(e.message, 'error'); btn.disabled = false; btn.textContent = 'Отменить билет'; }
}

async function loadAdminData() {
  try {
    const [movies, halls] = await Promise.all([api('GET', '/movies'), api('GET', '/halls')]);

    const mSel = document.getElementById('a-movie-id');
    mSel.innerHTML = movies.map(m => `<option value="${m.id}">${esc(m.title)}</option>`).join('');

    const hSel = document.getElementById('a-hall-id');
    hSel.innerHTML = halls.map(h => `<option value="${h.id}">${esc(h.name)}</option>`).join('');

    adminLoadTickets();
  } catch(e) {}
}

async function adminAddMovie() {
  const title  = document.getElementById('a-title').value.trim();
  const genre  = document.getElementById('a-genre').value.trim();
  const desc   = document.getElementById('a-desc').value.trim();
  const dur    = parseInt(document.getElementById('a-dur').value);
  const poster = document.getElementById('a-poster').value.trim();
  const rating = parseFloat(document.getElementById('a-rating').value);
  if (!title) { toast('Введите название', 'error'); return; }
  try {
    await api('POST', '/movies', { title, genre: genre||null, description: desc||null, duration: dur, poster_url: poster||null, rating });
    toast('✅ Фильм добавлен!');
    document.getElementById('a-title').value = '';
    loadMovies();
    loadAdminData();
  } catch(e) { toast(e.message, 'error'); }
}

async function adminAddSession() {
  const movie_id = parseInt(document.getElementById('a-movie-id').value);
  const hall_id  = parseInt(document.getElementById('a-hall-id').value);
  const time     = document.getElementById('a-time').value;
  const price    = parseFloat(document.getElementById('a-price').value);
  if (!time) { toast('Выберите время', 'error'); return; }
  try {
    await api('POST', '/sessions', { movie_id, hall_id, start_time: time.replace('T',' '), price });
    toast('✅ Сеанс добавлен!');
    document.getElementById('a-time').value = '';
  } catch(e) { toast(e.message, 'error'); }
}

async function adminLoadTickets() {
  const el = document.getElementById('admin-tickets');
  el.innerHTML = '<div class="loading-state"><div class="spinner"></div></div>';
  try {
    const tickets = await api('GET', '/tickets/all');
    if (!tickets.length) { el.innerHTML = '<p style="color:var(--muted);text-align:center;padding:20px">Билетов нет</p>'; return; }
    el.innerHTML = `
      <table class="admin-table">
        <thead><tr>
          <th>#</th><th>Пользователь</th><th>Фильм</th><th>Зал</th><th>Время</th><th>Место</th><th>Цена</th><th></th>
        </tr></thead>
        <tbody>
          ${tickets.map(t => {
            const dt = new Date(t.start_time);
            return `<tr>
              <td style="color:var(--muted)">#${t.id}</td>
              <td>${esc(t.username)}</td>
              <td>${esc(t.movie_title)}</td>
              <td>${esc(t.hall_name)}</td>
              <td>${dt.toLocaleDateString('ru',{day:'numeric',month:'short'})} ${dt.toLocaleTimeString('ru',{hour:'2-digit',minute:'2-digit'})}</td>
              <td style="color:var(--accent)">Р${t.seat_row} М${t.seat_col}</td>
              <td>${t.price.toLocaleString()} тг</td>
              <td><button onclick="cancelTicket(${t.id},this)" style="background:none;border:1px solid var(--border);border-radius:4px;color:var(--muted);padding:4px 8px;cursor:pointer;font-size:11px">✕</button></td>
            </tr>`;
          }).join('')}
        </tbody>
      </table>`;
  } catch(e) { el.innerHTML = '<p style="color:var(--red);text-align:center;padding:20px">Ошибка загрузки</p>'; }
}

async function api(method, url, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (token) opts.headers['Authorization'] = 'Bearer ' + token;
  if (body)  opts.body = JSON.stringify(body);
  const res  = await fetch(API + url, opts);
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Ошибка сервера');
  return data;
}

let tTimer;
function toast(msg, type = 'success') {
  const t = document.getElementById('toast');
  t.textContent = msg; t.className = 'toast ' + type + ' show';
  clearTimeout(tTimer); tTimer = setTimeout(() => t.classList.remove('show'), 3000);
}

function esc(s) {
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
