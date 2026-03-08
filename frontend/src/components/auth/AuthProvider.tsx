"use client";

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from "react";
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

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // On mount, check for stored token and validate it
  useEffect(() => {
    const stored = localStorage.getItem(TOKEN_KEY);
    if (stored) {
      setToken(stored);
      authApi
        .me(stored)
        .then((userData) => {
          setUser(userData as User);
        })
        .catch(() => {
          // Token invalid or backend unavailable — clear silently
          localStorage.removeItem(TOKEN_KEY);
          setToken(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setError(null);
    setIsLoading(true);
    try {
      const res = await authApi.login({ email, password });
      const accessToken = res.access_token;
      localStorage.setItem(TOKEN_KEY, accessToken);
      setToken(accessToken);

      const userData = await authApi.me(accessToken);
      setUser(userData as User);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Login failed";
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

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
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
    setError(null);
  }, []);

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
