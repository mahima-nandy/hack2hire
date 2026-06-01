const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export const tokenStore = {
  get access() {
    return localStorage.getItem("accessToken");
  },
  set(access: string, refresh: string) {
    localStorage.setItem("accessToken", access);
    localStorage.setItem("refreshToken", refresh);
  },
  clear() {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
  }
};

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const isForm = init.body instanceof FormData;
  if (!isForm) headers.set("Content-Type", "application/json");
  if (tokenStore.access) headers.set("Authorization", `Bearer ${tokenStore.access}`);
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers });
  if (!response.ok) {
    const text = await response.text();
    throw new ApiError(text || response.statusText, response.status);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

export const api = {
  signup: (payload: { username: string; email: string; password: string }) =>
    request<{ id: number; username: string }>("/auth/signup/", { method: "POST", body: JSON.stringify(payload) }),
  login: (payload: { username: string; password: string }) =>
    request<{ access: string; refresh: string }>("/auth/login/", { method: "POST", body: JSON.stringify(payload) }),
  list: <T>(path: string) => request<T[]>(`${path}/`),
  get: <T>(path: string, id: number) => request<T>(`${path}/${id}/`),
  post: <T>(path: string, body: unknown) => request<T>(`${path}/`, { method: "POST", body: JSON.stringify(body) }),
  upload: <T>(path: string, data: FormData) => request<T>(`${path}/`, { method: "POST", body: data }),
  action: <T>(path: string, id: number, action: string, body: unknown = {}) =>
    request<T>(`${path}/${id}/${action}/`, { method: "POST", body: JSON.stringify(body) }),
  answer: <T>(data: FormData) => request<T>("/answers/", { method: "POST", body: data }),
  analytics: () => request<unknown>("/analytics/summary/")
};

export function websocketUrl(sessionId: number) {
  const base = import.meta.env.VITE_WS_BASE_URL ?? "ws://localhost:8000";
  return `${base}/ws/interviews/${sessionId}/`;
}
