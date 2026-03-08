"use client";

import { createContext, useContext, useState, useEffect, useCallback, useRef, ReactNode } from "react";
import { auth as authApi } from "@/lib/api";

interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  role: string;
  avatar_url: string | null;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (data: { email: string; username: string; password: string; full_name: string }) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

const TOKEN_KEY = "cs_rankings_token";
const REFRESH_KEY = "cs_rankings_refresh";

// Refresh the access token 2 minutes before it expires (28 min for 30 min tokens)
const REFRESH_INTERVAL_MS = 28 * 60 * 1000;

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const refreshTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const clearRefreshTimer = useCallback(() => {
    if (refreshTimerRef.current) {
      clearInterval(refreshTimerRef.current);
      refreshTimerRef.current = null;
    }
  }, []);

  const storeTokens = useCallback((accessToken: string, refreshToken?: string) => {
    localStorage.setItem(TOKEN_KEY, accessToken);
    if (refreshToken) {
      localStorage.setItem(REFRESH_KEY, refreshToken);
    }
    setToken(accessToken);
  }, []);

  const clearTokens = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    setToken(null);
    setUser(null);
    clearRefreshTimer();
  }, [clearRefreshTimer]);

  // Schedule automatic token refresh
  const scheduleRefresh = useCallback(() => {
    clearRefreshTimer();
    refreshTimerRef.current = setInterval(async () => {
      const storedRefresh = localStorage.getItem(REFRESH_KEY);
      if (!storedRefresh) return;

      try {
        // Re-login silently using refresh token
        // Since the backend doesn't have a dedicated refresh endpoint,
        // we validate the current token and keep using it until expiry
        const currentToken = localStorage.getItem(TOKEN_KEY);
        if (currentToken) {
          await authApi.me(currentToken);
          // Token still valid, nothing to do
        }
      } catch {
        // Token expired and refresh failed — clear silently
        clearTokens();
      }
    }, REFRESH_INTERVAL_MS);
  }, [clearRefreshTimer, clearTokens]);

  // On mount, check for stored token and validate it
  useEffect(() => {
    const stored = localStorage.getItem(TOKEN_KEY);
    if (stored) {
      setToken(stored);
      authApi
        .me(stored)
        .then((userData) => {
          setUser(userData as User);
          scheduleRefresh();
        })
        .catch(() => {
          clearTokens();
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }

    return () => clearRefreshTimer();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const login = useCallback(async (email: string, password: string) => {
    setError(null);
    setIsLoading(true);
    try {
      const res = await authApi.login({ email, password });
      storeTokens(res.access_token, res.refresh_token);

      const userData = await authApi.me(res.access_token);
      setUser(userData as User);
      scheduleRefresh();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Login failed";
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [storeTokens, scheduleRefresh]);

  const register = useCallback(
    async (data: { email: string; username: string; password: string; full_name: string }) => {
      setError(null);
      setIsLoading(true);
      try {
        await authApi.register(data);
        // Auto-login after registration
        await login(data.email, data.password);
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Registration failed";
        setError(message);
        setIsLoading(false);
        throw err;
      }
    },
    [login]
  );

  const logout = useCallback(() => {
    clearTokens();
    setError(null);
  }, [clearTokens]);

  const clearError = useCallback(() => setError(null), []);

  return (
    <AuthContext.Provider value={{ user, token, isLoading, error, login, register, logout, clearError }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
