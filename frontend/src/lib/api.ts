const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface FetchOptions extends RequestInit {
  token?: string;
}

async function fetchApi<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
  const { token, ...fetchOptions } = options;

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${endpoint}`, {
    ...fetchOptions,
    headers,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

// Auth
export const auth = {
  register: (data: { email: string; username: string; password: string; full_name: string }) =>
    fetchApi("/auth/register", { method: "POST", body: JSON.stringify(data) }),
  login: (data: { email: string; password: string }) =>
    fetchApi<{ access_token: string; refresh_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  me: (token: string) => fetchApi("/auth/me", { token }),
};

// Athletes
export const athletes = {
  list: (params?: Record<string, string>) => {
    const query = params ? "?" + new URLSearchParams(params).toString() : "";
    return fetchApi(`/athletes${query}`);
  },
  get: (id: string) => fetchApi(`/athletes/${id}`),
  ratingHistory: (id: string, type = "overall") =>
    fetchApi(`/athletes/${id}/rating-history?rating_type=${type}`),
};

// Leaderboards
export const leaderboards = {
  global: (params?: Record<string, string>) => {
    const query = params ? "?" + new URLSearchParams(params).toString() : "";
    return fetchApi(`/leaderboards/global${query}`);
  },
  country: (code: string, params?: Record<string, string>) => {
    const query = params ? "?" + new URLSearchParams(params).toString() : "";
    return fetchApi(`/leaderboards/country/${code}${query}`);
  },
};

// Events
export const events = {
  list: (params?: Record<string, string>) => {
    const query = params ? "?" + new URLSearchParams(params).toString() : "";
    return fetchApi(`/events${query}`);
  },
  get: (id: string) => fetchApi(`/events/${id}`),
  matches: (id: string) => fetchApi(`/events/${id}/matches`),
};

// Gyms
export const gyms = {
  list: (params?: Record<string, string>) => {
    const query = params ? "?" + new URLSearchParams(params).toString() : "";
    return fetchApi(`/gyms${query}`);
  },
  get: (id: string) => fetchApi(`/gyms/${id}`),
  athletes: (id: string) => fetchApi(`/gyms/${id}/athletes`),
};

// Social
export const social = {
  feed: (params?: Record<string, string>) => {
    const query = params ? "?" + new URLSearchParams(params).toString() : "";
    return fetchApi(`/social/feed${query}`);
  },
  createPost: (data: any, token: string) =>
    fetchApi("/social/posts", { method: "POST", body: JSON.stringify(data), token }),
  toggleLike: (postId: string, token: string) =>
    fetchApi(`/social/posts/${postId}/like`, { method: "POST", token }),
  getComments: (postId: string) => fetchApi(`/social/posts/${postId}/comments`),
  createComment: (postId: string, data: any, token: string) =>
    fetchApi(`/social/posts/${postId}/comments`, {
      method: "POST",
      body: JSON.stringify(data),
      token,
    }),
};

// Admin
export const admin = {
  dashboard: (token: string) => fetchApi("/admin/dashboard", { token }),
  users: (token: string, params?: Record<string, string>) => {
    const query = params ? "?" + new URLSearchParams(params).toString() : "";
    return fetchApi(`/admin/users${query}`, { token });
  },
  adjustElo: (athleteId: string, data: any, token: string) =>
    fetchApi(`/admin/athletes/${athleteId}/adjust-elo`, {
      method: "POST",
      body: JSON.stringify(data),
      token,
    }),
  recalculate: (token: string) =>
    fetchApi("/admin/recalculate-rankings", { method: "POST", token }),
  mergeAthletes: (data: any, token: string) =>
    fetchApi("/admin/athletes/merge", { method: "POST", body: JSON.stringify(data), token }),
};
