/**
 * Sentinel AI — Auth Store
 *
 * Lightweight auth state manager using React context.
 * Persists JWT + user to localStorage, provides login/logout/register.
 */

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import { authService, type AuthUser } from "@/lib/api-services";
import { extractError } from "@/lib/api-client";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
interface AuthState {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthActions {
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    username: string;
    password: string;
    full_name?: string;
  }) => Promise<void>;
  logout: () => void;
  refreshProfile: () => Promise<void>;
}

type AuthContextValue = AuthState & AuthActions;

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------
const AuthContext = createContext<AuthContextValue | null>(null);

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function loadToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("sentinel_token");
}

function loadUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem("sentinel_user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function persist(token: string, user: AuthUser) {
  localStorage.setItem("sentinel_token", token);
  localStorage.setItem("sentinel_user", JSON.stringify(user));
}

function clearStorage() {
  localStorage.removeItem("sentinel_token");
  localStorage.removeItem("sentinel_user");
}

// ---------------------------------------------------------------------------
// Provider
// ---------------------------------------------------------------------------
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(loadUser);
  const [token, setToken] = useState<string | null>(loadToken);
  const [isLoading, setIsLoading] = useState(false);

  const isAuthenticated = !!token && !!user;

  // Validate token on mount by fetching profile
  useEffect(() => {
    if (token && !user) {
      setIsLoading(true);
      authService
        .getProfile()
        .then((profile) => {
          setUser(profile);
          localStorage.setItem("sentinel_user", JSON.stringify(profile));
        })
        .catch(() => {
          clearStorage();
          setToken(null);
          setUser(null);
        })
        .finally(() => setIsLoading(false));
    }
  }, [token, user]);

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const res = await authService.login({ email, password });
      persist(res.access_token, res.user);
      setToken(res.access_token);
      setUser(res.user);
    } catch (err) {
      throw new Error(extractError(err));
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(
    async (data: {
      email: string;
      username: string;
      password: string;
      full_name?: string;
    }) => {
      setIsLoading(true);
      try {
        const res = await authService.register(data);
        persist(res.access_token, res.user);
        setToken(res.access_token);
        setUser(res.user);
      } catch (err) {
        throw new Error(extractError(err));
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  const logout = useCallback(() => {
    clearStorage();
    setToken(null);
    setUser(null);
  }, []);

  const refreshProfile = useCallback(async () => {
    try {
      const profile = await authService.getProfile();
      setUser(profile);
      localStorage.setItem("sentinel_user", JSON.stringify(profile));
    } catch {
      /* silent */
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, token, isAuthenticated, isLoading, login, register, logout, refreshProfile }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within <AuthProvider>");
  return ctx;
}
