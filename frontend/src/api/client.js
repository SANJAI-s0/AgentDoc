import axios from "axios";

const normalizeBase = (value) => value.replace(/\/+$/, "");

const API_BASE = (() => {
  const configured = import.meta.env.VITE_API_BASE;
  if (configured) return normalizeBase(configured);
  if (typeof window !== "undefined" && window.location.port === "5173") return "http://localhost:8000/api";
  if (typeof window !== "undefined") return `${window.location.origin}/api`;
  return "http://localhost:8000/api";
})();

const ACCESS_TOKEN_KEY = "agentdoc.access_token";
const REFRESH_TOKEN_KEY = "agentdoc.refresh_token";

const readAccessToken = () => (typeof window === "undefined" ? "" : window.localStorage.getItem(ACCESS_TOKEN_KEY) || "");
const readRefreshToken = () => (typeof window === "undefined" ? "" : window.localStorage.getItem(REFRESH_TOKEN_KEY) || "");

const saveTokens = (payload) => {
  if (typeof window === "undefined") return;
  if (payload?.access) window.localStorage.setItem(ACCESS_TOKEN_KEY, payload.access);
  if (payload?.refresh) window.localStorage.setItem(REFRESH_TOKEN_KEY, payload.refresh);
};

const clearTokens = () => {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_TOKEN_KEY);
};

const client = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
});

let refreshingPromise = null;

client.interceptors.request.use((config) => {
  const token = readAccessToken();
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (!original || original._retry || error?.response?.status !== 401) {
      return Promise.reject(error);
    }

    if (original.url?.includes("/auth/login") || original.url?.includes("/auth/refresh")) {
      return Promise.reject(error);
    }

    const refresh = readRefreshToken();
    if (!refresh) {
      clearTokens();
      return Promise.reject(error);
    }

    if (!refreshingPromise) {
      refreshingPromise = client
        .post("/auth/refresh/", { refresh })
        .then((response) => {
          saveTokens(response.data);
          return response.data.access;
        })
        .catch((refreshError) => {
          clearTokens();
          throw refreshError;
        })
        .finally(() => {
          refreshingPromise = null;
        });
    }

    try {
      const newAccess = await refreshingPromise;
      original._retry = true;
      original.headers = original.headers || {};
      original.headers.Authorization = `Bearer ${newAccess}`;
      return client(original);
    } catch (refreshError) {
      return Promise.reject(refreshError);
    }
  }
);

const unwrap = async (promise) => {
  try {
    const response = await promise;
    return response.data;
  } catch (error) {
    const detail =
      error?.response?.data?.detail ||
      error?.response?.data?.message ||
      error?.message ||
      "Request failed";
    const wrapped = new Error(detail);
    wrapped.status = error?.response?.status;
    wrapped.payload = error?.response?.data;
    throw wrapped;
  }
};

export const api = {
  getSession: () => unwrap(client.get("/auth/me/")),
  login: async (payload) => {
    const data = await unwrap(client.post("/auth/login/", payload));
    saveTokens(data);
    return data;
  },
  logout: async () => {
    const refresh = readRefreshToken();
    try {
      await unwrap(client.post("/auth/logout/", { refresh }));
    } finally {
      clearTokens();
    }
  },
  getDashboard: () => unwrap(client.get("/dashboard/")),
  getDocuments: () => unwrap(client.get("/documents/")),
  getDocumentDetail: (documentId) => unwrap(client.get(`/documents/${documentId}/`)),
  getDocumentStatus: (documentId) => unwrap(client.get(`/documents/${documentId}/status/`)),
  getDocumentExtraction: (documentId) => unwrap(client.get(`/documents/${documentId}/extraction/`)),
  getDocumentAudit: (documentId) => unwrap(client.get(`/audit/${documentId}/`)),
  getReviews: () => unwrap(client.get("/reviews/")),
  triggerReview: (payload) => unwrap(client.post("/trigger-review/", payload)),
  searchDocuments: (query, limit = 10) => unwrap(client.get(`/search/semantic/?q=${encodeURIComponent(query)}&limit=${limit}`)),
  getHealth: () => unwrap(client.get("/health/")),
  requestUploadUrl: (payload) => unwrap(client.post("/documents/upload-url/", payload)),
  uploadToPresignedUrl: async (uploadUrl, file, onProgress) =>
    unwrap(
      axios.put(uploadUrl, file, {
        headers: { "Content-Type": file?.type || "application/octet-stream" },
        onUploadProgress: (progressEvent) => {
          if (!onProgress || !progressEvent.total) return;
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percent);
        },
      })
    ),
  uploadDocument: (formData, onProgress) =>
    unwrap(
      client.post("/documents/upload/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (progressEvent) => {
          if (!onProgress || !progressEvent.total) return;
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percent);
        },
      })
    ),
  submitReviewByDocument: (documentId, payload) => unwrap(client.post(`/reviews/${documentId}/action/`, payload)),
  submitReviewByReviewId: (reviewId, payload) => unwrap(client.post(`/reviews/${reviewId}/submit/`, payload)),
};

export { API_BASE, clearTokens, readAccessToken, readRefreshToken, saveTokens };
