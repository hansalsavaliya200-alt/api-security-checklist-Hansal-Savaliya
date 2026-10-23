let accessToken = '';
let visibleNotes = [];

const authStatus = document.getElementById('authStatus');
const healthInfo = document.getElementById('healthInfo');
const notesList = document.getElementById('notesList');
const loginForm = document.getElementById('loginForm');
const noteForm = document.getElementById('noteForm');
const logoutBtn = document.getElementById('logoutBtn');
const refreshBtn = document.getElementById('refreshBtn');
const themeBtn = document.getElementById('themeBtn');

function authHeaders() {
  return accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
}

function setAuthState(isLoggedIn, username = '') {
  const loggedIn = Boolean(isLoggedIn && username);
  logoutBtn.classList.toggle('hidden', !loggedIn);
  noteForm.classList.toggle('hidden', !loggedIn);
  document.querySelector('#loginForm button').disabled = loggedIn;
  if (loggedIn) {
    authStatus.textContent = `Signed in as ${username}.`;
    authStatus.className = 'status success';
  } else {
    authStatus.textContent = 'Not signed in.';
    authStatus.className = 'status neutral';
  }
}

function updateRateMetrics(response) {
  const remaining = response.headers.get('X-RateLimit-Remaining');
  const reset = response.headers.get('X-RateLimit-Reset');
  document.getElementById('rateRemaining').textContent = remaining ?? '—';
  document.getElementById('rateReset').textContent = reset === null ? '—' : `${reset}s`;
}

async function fetchJson(url, options = {}) {
  const { headers: customHeaders = {}, ...requestOptions } = options;
  const headers = {
    Accept: 'application/json',
    ...(requestOptions.body ? { 'Content-Type': 'application/json' } : {}),
    ...customHeaders,
  };
  const response = await fetch(url, { ...requestOptions, headers });
  updateRateMetrics(response);

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.error?.message || 'Request failed.');
  }
  return payload;
}

async function loadHealth() {
  const status = document.getElementById('apiStatus');
  try {
    const data = await fetchJson('/api/v1/health');
    status.textContent = 'Operational';
    status.className = 'status-pill online';
    document.getElementById('uptime').textContent = formatDuration(data.uptime_seconds);
    healthInfo.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    status.textContent = 'Unavailable';
    status.className = 'status-pill offline';
    document.getElementById('uptime').textContent = '—';
    healthInfo.textContent = `Error: ${error.message}`;
  }
}

async function loadProfile() {
  if (!accessToken) {
    setAuthState(false);
    return;
  }

  try {
    const data = await fetchJson('/api/v1/me', { headers: authHeaders() });
    setAuthState(true, data.username);
  } catch (error) {
    accessToken = '';
    setAuthState(false);
    authStatus.textContent = error.message;
    authStatus.className = 'status danger';
  }
}

function renderActivityChart(notes) {
  const chart = document.getElementById('activityChart');
  const caption = document.getElementById('chartCaption');
  const today = new Date();
  const days = Array.from({ length: 7 }, (_, index) => {
    const date = new Date(today);
    date.setHours(0, 0, 0, 0);
    date.setDate(date.getDate() - (6 - index));
    return date;
  });
  const counts = days.map((day) => {
    const nextDay = new Date(day);
    nextDay.setDate(nextDay.getDate() + 1);
    return notes.filter((note) => {
      const createdAt = note.created_at * 1000;
      return createdAt >= day.getTime() && createdAt < nextDay.getTime();
    }).length;
  });
  const maxCount = Math.max(1, ...counts);
  chart.innerHTML = days.map((day, index) => {
    const level = Math.max(1, Math.ceil((counts[index] / maxCount) * 10));
    const label = day.toLocaleDateString(undefined, { weekday: 'short' });
    return `<div class="chart-column" title="${counts[index]} note(s)">
      <span class="chart-value">${counts[index]}</span>
      <div class="chart-track"><div class="chart-bar bar-level-${level}"></div></div>
      <span class="chart-label">${label}</span>
    </div>`;
  }).join('');
  caption.textContent = `Based on ${notes.length} notes loaded`;
}

async function loadNotes() {
  if (!accessToken) {
    visibleNotes = [];
    document.getElementById('noteCount').textContent = '—';
    notesList.innerHTML = '<li class="empty">Sign in to view notes.</li>';
    renderActivityChart([]);
    document.getElementById('chartCaption').textContent = 'Sign in to view activity';
    return;
  }

  try {
    const data = await fetchJson('/api/v1/notes?limit=50', { headers: authHeaders() });
    visibleNotes = data.items || [];
    document.getElementById('noteCount').textContent = String(data.total ?? visibleNotes.length);
    renderActivityChart(visibleNotes);
    if (!visibleNotes.length) {
      notesList.innerHTML = '<li class="empty">No notes yet.</li>';
      return;
    }

    notesList.innerHTML = visibleNotes.map((note) => `
      <li class="note-item" data-note-id="${escapeHtml(note.id)}">
        <div class="note-content">
          <h3>${escapeHtml(note.title)}</h3>
          <p>${escapeHtml(note.body)}</p>
          <small>${new Date(note.created_at * 1000).toLocaleString()}</small>
        </div>
        <div class="note-actions">
          <button class="secondary edit-note" type="button">Edit</button>
          <button class="danger-button delete-note" type="button">Delete</button>
        </div>
      </li>
    `).join('');
  } catch (error) {
    notesList.innerHTML = `<li class="empty">${escapeHtml(error.message)}</li>`;
  }
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function formatDuration(seconds) {
  const total = Math.floor(Number(seconds) || 0);
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const remainingSeconds = total % 60;
  if (hours) return `${hours}h ${minutes}m`;
  if (minutes) return `${minutes}m ${remainingSeconds}s`;
  return `${remainingSeconds}s`;
}

function showActionError(error) {
  authStatus.textContent = error.message;
  authStatus.className = 'status danger';
}

loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(loginForm);
  const payload = {
    username: String(formData.get('username') || '').trim(),
    password: String(formData.get('password') || ''),
  };

  try {
    const data = await fetchJson('/api/v1/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    accessToken = data.access_token;
    setAuthState(true, payload.username);
    await loadNotes();
  } catch (error) {
    showActionError(error);
  }
});

noteForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(noteForm);
  const payload = {
    title: String(formData.get('title') || '').trim(),
    body: String(formData.get('body') || '').trim(),
  };

  try {
    await fetchJson('/api/v1/notes', {
      method: 'POST',
      body: JSON.stringify(payload),
      headers: authHeaders(),
    });
    noteForm.reset();
    await loadNotes();
  } catch (error) {
    showActionError(error);
  }
});

notesList.addEventListener('click', async (event) => {
  const button = event.target.closest('button');
  if (!button) return;
  const item = button.closest('[data-note-id]');
  const note = visibleNotes.find((entry) => entry.id === item?.dataset.noteId);
  if (!note) return;

  try {
    if (button.classList.contains('edit-note')) {
      const title = window.prompt('Update note title:', note.title);
      if (title === null) return;
      const body = window.prompt('Update note body:', note.body);
      if (body === null) return;
      await fetchJson(`/api/v1/notes/${encodeURIComponent(note.id)}`, {
        method: 'PUT',
        headers: authHeaders(),
        body: JSON.stringify({ title: title.trim(), body: body.trim() }),
      });
      await loadNotes();
    } else if (button.classList.contains('delete-note') &&
               window.confirm(`Delete "${note.title}"? This cannot be undone.`)) {
      await fetchJson(`/api/v1/notes/${encodeURIComponent(note.id)}`, {
        method: 'DELETE',
        headers: authHeaders(),
      });
      await loadNotes();
    }
  } catch (error) {
    showActionError(error);
  }
});

logoutBtn.addEventListener('click', () => {
  accessToken = '';
  setAuthState(false);
  loadNotes();
});

refreshBtn.addEventListener('click', async () => {
  await Promise.all([loadHealth(), loadNotes()]);
});

themeBtn.addEventListener('click', () => {
  const isDark = document.documentElement.dataset.theme !== 'dark';
  document.documentElement.dataset.theme = isDark ? 'dark' : 'light';
  themeBtn.textContent = isDark ? 'Light mode' : 'Dark mode';
  themeBtn.setAttribute('aria-pressed', String(isDark));
  localStorage.setItem('demo-api-theme', isDark ? 'dark' : 'light');
});

(async function init() {
  const theme = localStorage.getItem('demo-api-theme');
  if (theme === 'dark') {
    document.documentElement.dataset.theme = 'dark';
    themeBtn.textContent = 'Light mode';
    themeBtn.setAttribute('aria-pressed', 'true');
  }
  setAuthState(false);
  noteForm.classList.add('hidden');
  await loadHealth();
  await loadNotes();
})();
