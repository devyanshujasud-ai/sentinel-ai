/**
 * Sentinel AI — Axios API Client
 *
 * Configured singleton with:
 * - Base URL from environment variable
 * - JWT auth interceptor (reads from localStorage)
 * - Automatic 401 redirect to /login
 * - Structured error extraction
 */

import axios, {
  type AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------
const API_BASE_URL =
  (typeof import.meta !== "undefined" &&
    (import.meta as Record<string, Record<string, string>>).env
      ?.VITE_API_BASE_URL) ||
  "http://localhost:8000/api/v1";

// ---------------------------------------------------------------------------
// Client factory
// ---------------------------------------------------------------------------
function createApiClient(): AxiosInstance {
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30_000,
    headers: { "Content-Type": "application/json" },
  });

  // -- Request interceptor: attach JWT ---------------------------------
  client.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      if (typeof window !== "undefined") {
        const token = localStorage.getItem("sentinel_token");
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      }
      return config;
    },
    (error) => Promise.reject(error),
  );

  // -- Response interceptor: handle 401 --------------------------------
  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError<{ detail?: string }>) => {
      if (error.response?.status === 401 && typeof window !== "undefined") {
        localStorage.removeItem("sentinel_token");
        localStorage.removeItem("sentinel_user");
        // Redirect to login if not already there
        if (!window.location.pathname.includes("/login")) {
          window.location.href = "/login";
        }
      }
      return Promise.reject(error);
    },
  );

  return client;
}

// ---------------------------------------------------------------------------
// Singleton export
// ---------------------------------------------------------------------------
export const api = createApiClient();

// ---------------------------------------------------------------------------
// Error helper
// ---------------------------------------------------------------------------
export function extractError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data;
    if (typeof data?.detail === "string") return data.detail;
    if (Array.isArray(data?.detail)) {
      return data.detail.map((d: { msg: string }) => d.msg).join(", ");
    }
    if (error.response?.status === 429) return "Rate limit exceeded. Please slow down.";
    if (error.response?.status === 500) return "Internal server error. Please try again.";
    if (error.code === "ECONNABORTED") return "Request timed out. Please try again.";
    if (!error.response) return "Cannot reach server. Check your connection.";
    return error.message;
  }
  if (error instanceof Error) return error.message;
  return "An unexpected error occurred.";
}
