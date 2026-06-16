import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Interceptor: inject JWT token if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('edubot_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ─── Chat API ────────────────────────────────────────────────────
export const sendChatMessage = async (message, sessionId = null) => {
  const response = await api.post('/chat/send', {
    message,
    session_id: sessionId,
  });
  return response.data;
};

export const sendAudioMessage = async (audioBlob, sessionId = null) => {
  const formData = new FormData();
  formData.append('file', audioBlob, 'audio.webm');
  if (sessionId) formData.append('session_id', sessionId);

  const response = await api.post('/chat/voice', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000,
  });
  return response.data;
};

export const getChatHistory = async (sessionId) => {
  const response = await api.get('/chat/history', {
    params: { session_id: sessionId },
  });
  return response.data;
};

// ─── Filières API ────────────────────────────────────────────────
export const getFilieres = async ({ domaine, search, limit = 20, skip = 0 } = {}) => {
  const response = await api.get('/filieres', {
    params: { domaine, search, limit, skip },
  });
  return response.data;
};

export const getFiliere = async (id) => {
  const response = await api.get(`/filieres/${id}`);
  return response.data;
};

export const compareFilieres = async (filiereIds) => {
  const response = await api.post('/filieres/compare', {
    filiere_ids: filiereIds,
  });
  return response.data;
};

// ─── Upload / OCR API ────────────────────────────────────────────
export const uploadTranscript = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload/transcript', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000,
  });
  return response.data;
};

// ─── Auth API ────────────────────────────────────────────────────
export const register = async ({ email, password, full_name }) => {
  const response = await api.post('/auth/register', {
    email,
    password,
    full_name,
  });
  if (response.data.token) {
    localStorage.setItem('edubot_token', response.data.token);
  }
  return response.data;
};

export const login = async (email, password) => {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const response = await api.post('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  if (response.data.access_token) {
    localStorage.setItem('edubot_token', response.data.access_token);
  }
  return response.data;
};

export const getMe = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

export const logout = () => {
  localStorage.removeItem('edubot_token');
};

export default api;
