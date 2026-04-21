import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_GATEWAY_URL !== undefined 
  ? process.env.REACT_APP_API_GATEWAY_URL 
  : 'http://localhost:8000';
const API_VERSION = process.env.REACT_APP_API_VERSION || 'v1';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/${API_VERSION}`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
api.interceptors.request.use(
  (config) => {
    const apiKey = process.env.REACT_APP_API_KEY;
    if (apiKey) {
      config.headers.Authorization = `Bearer ${apiKey}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// =============================================================================
// Dashboard API
// =============================================================================
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  getActivity: () => api.get('/dashboard/activity'),
  getPillars: () => api.get('/dashboard/pillars'),
  getPerformance: () => api.get('/dashboard/performance'),
};

// =============================================================================
// Pillar A: RAG Knowledge Base API
// =============================================================================
export const pillarAAPI = {
  searchFunds: (query) => api.get('/funds/search', { params: { query } }),
  queryRAG: (data) => api.post('/query', data),
  getSources: () => api.get('/sources'),
};

// =============================================================================
// Pillar B: Weekly Pulse API
// =============================================================================
export const pillarBAPI = {
  getWeeklyPulse: () => api.get('/pillar-b/weekly-pulse'),
  getThemes: () => api.get('/pillar-b/themes'),
  getAnalytics: () => api.get('/pillar-b/analytics'),
  getThemeTrends: (themeId) => api.get(`/pillar-b/analytics/themes/${themeId}`),
  getSentiment: () => api.get('/pillar-b/analytics/sentiment'),
  getVolume: () => api.get('/pillar-b/analytics/volume'),
  getKeywords: () => api.get('/pillar-b/analytics/keywords'),
  refreshAnalysis: () => api.post('/pillar-b/refresh'),
  downloadReviewsCSV: () => api.get('/pillar-b/reviews/download', { responseType: 'blob' }),
};

// =============================================================================
// Pillar C: Voice Agent API
// =============================================================================
export const pillarCAPI = {
  startRecording: (sessionId = null) => api.post('/pillar-c/voice/record/start', { session_id: sessionId }),
  stopRecording: (recordingId) => api.post('/pillar-c/voice/record/stop', { recording_id: recordingId }),
  cancelRecording: (recordingId) => api.post('/pillar-c/voice/record/cancel', { recording_id: recordingId }),
  playAudio: (audioId) => api.get(`/pillar-c/voice/play/${audioId}`),
  playTTS: (text) => api.post('/pillar-c/tts/play', { text }),
  getPipelineStatus: () => api.get('/pillar-c/pipeline/status'),
  sendMessage: (message) => api.post('/pillar-c/conversation/message', { message }),
  sendVoiceMessage: (audioBase64) => api.post('/pillar-c/conversation/voice', { audio_base64: audioBase64 }),
};

// =============================================================================
// HITL: Approval Center API
// =============================================================================
export const hitlAPI = {
  getPending: () => api.get('/hitl/pending'),
  getActions: () => api.get('/hitl/actions'),
  getEmailPreview: (bookingCode) => api.get(`/hitl/email/preview/${bookingCode}`),
  sendEmail: (bookingCode, data) => api.post(`/hitl/email/send/${bookingCode}`, data),
  editEmail: (bookingCode, data) => api.post(`/hitl/email/edit/${bookingCode}`, data),
  approveAction: (actionId) => api.post(`/hitl/approve/${actionId}`),
  rejectAction: (actionId) => api.post(`/hitl/reject/${actionId}`),
};

// =============================================================================
// Evals: Testing API
// =============================================================================
export const evalsAPI = {
  runRAGEval: () => api.post('/evals/rag'),
  runSafetyEval: () => api.post('/evals/safety'),
  runUXEval: () => api.post('/evals/ux'),
  runIntegrationEval: () => api.post('/evals/integration'),
  getResults: () => api.get('/evals/results'),
};

export default api;
