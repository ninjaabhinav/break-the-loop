const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getToken() {
  return localStorage.getItem("btl_token");
}

async function request(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (response.status === 204) return null;

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const message = data?.detail || `Request failed (${response.status})`;
    throw new Error(typeof message === "string" ? message : "Request failed");
  }
  return data;
}

export const api = {
  register: (payload) => request("/api/auth/register", { method: "POST", body: payload, auth: false }),
  login: (payload) => request("/api/auth/login", { method: "POST", body: payload, auth: false }),
  me: () => request("/api/auth/me"),

  listLoops: () => request("/api/loops"),
  createLoop: (payload) => request("/api/loops", { method: "POST", body: payload }),
  updateLoop: (id, payload) => request(`/api/loops/${id}`, { method: "PATCH", body: payload }),
  deleteLoop: (id) => request(`/api/loops/${id}`, { method: "DELETE" }),

  onboardingHistory: () => request("/api/onboarding/history"),
  sendOnboardingMessage: (message) =>
    request("/api/onboarding/message", { method: "POST", body: { message } }),

  listInterventions: () => request("/api/interventions"),
  retrainModel: () => request("/api/interventions/retrain-model", { method: "POST" }),

  logUrge: (payload) => request("/api/events/urge", { method: "POST", body: payload }),
  selectIntervention: (eventId, interventionId) =>
    request(`/api/events/${eventId}/select`, {
      method: "PATCH",
      body: { intervention_selected_id: interventionId },
    }),
  reportOutcome: (eventId, payload) =>
    request(`/api/events/${eventId}/outcome`, { method: "PATCH", body: payload }),
  listEvents: (loopId) => request(`/api/events${loopId ? `?loop_id=${loopId}` : ""}`),

  getAnalytics: (loopId) => request(`/api/analytics${loopId ? `?loop_id=${loopId}` : ""}`),
};

export { getToken };
