const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  const text = await response.text();
  const payload = text ? JSON.parse(text) : null;

  if (!response.ok) {
    const message = payload?.detail || payload?.error || 'Request failed';
    throw new Error(message);
  }

  return payload;
}

export { API_BASE_URL };

export function registerUser(payload) {
  return request('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function loginUser(payload) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function restoreSession(sessionToken) {
  return request(`/auth/session/${sessionToken}`);
}

export function logoutUser(sessionToken) {
  return request(`/auth/logout?session_token=${encodeURIComponent(sessionToken)}`, {
    method: 'POST',
  });
}

export function submitTrainingRound(payload) {
  return request('/train', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function predictTyping(payload) {
  return request('/predict', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
