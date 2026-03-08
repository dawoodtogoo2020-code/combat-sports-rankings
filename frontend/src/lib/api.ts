const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

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

/** Upload a file via multipart/form-data (XHR for progress tracking) */
async function uploadFile<T>(
  endpoint: string,
  file: File,
  token: string,
  onProgress?: (pct: number) => void
): Promise<T> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API_URL}${endpoint}`);
    xhr.setRequestHeader("Authorization", `Bearer ${token}`);

    if (onProgress) {
      xhr.upload.addEventListener("progress", (e) => {
        if (e.lengthComputable) onProgress(Math.round((e.loaded / e.total) * 100));
      });
    }

    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        try {
          const err = JSON.parse(xhr.responseText);
          reject(new Error(err.detail || `Upload failed (${xhr.status})`));
        } catch {
          reject(new Error(`Upload failed (${xhr.status})`));
        }
      }
    });

    xhr.addEventListener("error", () => reject(new Error("Upload failed — network error")));
    xhr.addEventListener("abort", () => reject(new Error("Upload cancelled")));

    const formData = new FormData();
    formData.append("file", file);
    xhr.send(formData);
  });
}

/** Resolve a media URL — handles both absolute and relative API paths */
export function mediaUrl(path: string): string {
  if (path.startsWith("http")) return path;
  return `${API_BASE}${path}`;
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

// Upload
export const upload = {
  media: (file: File, token: string, onProgress?: (pct: number) => void) =>
    uploadFile<{ url: string; filename: string; content_type: string; size: number }>(
      "/upload/media",
      file,
      token,
      onProgress
    ),
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
  adjustElo: (athleteId: string, data: { new_rating: number; reason: string }, token: string) =>
    fetchApi(`/admin/athletes/${athleteId}/adjust-elo`, {
      method: "POST",
      body: JSON.stringify(data),
      token,
    }),
  recalculate: (token: string) =>
    fetchApi("/admin/recalculate-rankings", { method: "POST", token }),
  mergeAthletes: (data: { primary_athlete_id: string; duplicate_athlete_id: string }, token: string) =>
    fetchApi("/admin/athletes/merge", { method: "POST", body: JSON.stringify(data), token }),
  verifyMatch: (matchId: string, token: string) =>
    fetchApi(`/admin/matches/${matchId}/verify`, { method: "PATCH", token }),
  rejectMatch: (matchId: string, data: { reason: string }, token: string) =>
    fetchApi(`/admin/matches/${matchId}/reject`, { method: "PATCH", body: JSON.stringify(data), token }),
  verifyGym: (gymId: string, token: string) =>
    fetchApi(`/admin/gyms/${gymId}/verify`, { method: "POST", token }),
  moderatePost: (postId: string, token: string) =>
    fetchApi(`/admin/posts/${postId}`, { method: "DELETE", token }),
  auditLog: (token: string, params?: Record<string, string>) => {
    const query = params ? "?" + new URLSearchParams(params).toString() : "";
    return fetchApi(`/admin/audit-log${query}`, { token });
  },
  dataSources: (token: string) => fetchApi("/admin/data-sources", { token }),
  updateDataSource: (sourceId: string, data: { is_active: boolean }, token: string) =>
    fetchApi(`/admin/data-sources/${sourceId}`, { method: "PATCH", body: JSON.stringify(data), token }),
  findDuplicates: (token: string) => fetchApi("/admin/athletes/duplicates", { token }),
  importCsv: (file: File, token: string, onProgress?: (pct: number) => void) =>
    uploadFile<{ message: string; events_imported: number; matches_imported: number; athletes_created: number }>(
      "/admin/import-csv",
      file,
      token,
      onProgress
    ),
};
