"use client";

import { createContext, useContext, useState, useEffect, useCallback, useRef, ReactNode } from "react";
import { auth as authApi } from "@/lib/api";
import { getSupabase, isSupabaseEnabled } from "@/lib/supabase";

interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  role: string;
  avatar_url: string | null;
  is_active: boolean;
}

type OAuthProvider = "google" | "github";

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  supabaseEnabled: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: { email: string; username: string; password: string; full_name: string }) => Promise<void>;
  signInWithOAuth: (provider: OAuthProvider) => Promise<void>;
  signInWithMagicLink: (email: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

const TOKEN_KEY = "cs_rankings_token";
const REFRESH_KEY = "cs_rankings_refresh";
const REFRESH_INTERVAL_MS = 28 * 60 * 1000;

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const refreshTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const supabaseEnabled = isSupabaseEnabled();

  const clearRefreshTimer = useCallback(() => {
    if (refreshTimerRef.current) {
      clearInterval(refreshTimerRef.current);
      refreshTimerRef.current = null;
    }
  }, []);

  const storeTokens = useCallback((accessToken: string, refreshToken?: string) => {
    localStorage.setItem(TOKEN_KEY, accessToken);
    if (refreshToken) localStorage.setItem(REFRESH_KEY, refreshToken);
    setToken(accessToken);
  }, []);

  const clearTokens = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    setToken(null);
    setUser(null);
    clearRefreshTimer();
  }, [clearRefreshTimer]);

  const scheduleRefresh = useCallback(() => {
    clearRefreshTimer();
    refreshTimerRef.current = setInterval(async () => {
      try {
        const currentToken = localStorage.getItem(TOKEN_KEY);
        if (currentToken) {
          await authApi.me(currentToken);
        }
      } catch {
        clearTokens();
      }
    }, REFRESH_INTERVAL_MS);
  }, [clearRefreshTimer, clearTokens]);

  // Bootstrap: check stored token, also check for a Supabase session (handles
  // OAuth redirect flows where the browser comes back with a fragment-encoded
  // session that Supabase auto-detects).
  useEffect(() => {
    let cancelled = false;

    const bootstrap = async () => {
      // 1) Already have our JWT? Validate it.
      const stored = localStorage.getItem(TOKEN_KEY);
      if (stored) {
        setToken(stored);
        try {
          const userData = await authApi.me(stored);
          if (cancelled) return;
          setUser(userData as User);
          scheduleRefresh();
          setIsLoading(false);
          return;
        } catch {
          if (cancelled) return;
          clearTokens();
        }
      }

      // 2) No JWT — check if Supabase has a fresh session (e.g. from OAuth callback)
      const sb = getSupabase();
      if (sb) {
        const { data } = await sb.auth.getSession();
        const sbToken = data.session?.access_token;
        if (sbToken && !cancelled) {
          try {
            const tokens = await authApi.supabase(sbToken);
            if (cancelled) return;
            storeTokens(tokens.access_token, tokens.refresh_token);
            const userData = await authApi.me(tokens.access_token);
            if (cancelled) return;
            setUser(userData as User);
            scheduleRefresh();
          } catch (e) {
            console.warn("Supabase token exchange failed during bootstrap", e);
          }
        }
      }

      if (!cancelled) setIsLoading(false);
    };

    bootstrap();
    return () => {
      cancelled = true;
      clearRefreshTimer();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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

  const signInWithOAuth = useCallback(async (provider: OAuthProvider) => {
    setError(null);
    const sb = getSupabase();
    if (!sb) {
      setError("Social sign-in is not configured");
      throw new Error("Supabase not configured");
    }
    const { error: oauthError } = await sb.auth.signInWithOAuth({
      provider,
      options: {
        redirectTo: typeof window !== "undefined" ? `${window.location.origin}/auth/callback` : undefined,
      },
    });
    if (oauthError) {
      setError(oauthError.message);
      throw oauthError;
    }
    // Browser will redirect away; bootstrap effect picks up the session on return.
  }, []);

  const signInWithMagicLink = useCallback(async (email: string) => {
    setError(null);
    const sb = getSupabase();
    if (!sb) {
      setError("Magic-link sign-in is not configured");
      throw new Error("Supabase not configured");
    }
    const { error: magicError } = await sb.auth.signInWithOtp({
      email,
      options: {
        emailRedirectTo: typeof window !== "undefined" ? `${window.location.origin}/auth/callback` : undefined,
      },
    });
    if (magicError) {
      setError(magicError.message);
      throw magicError;
    }
  }, []);

  const logout = useCallback(() => {
    const sb = getSupabase();
    if (sb) {
      sb.auth.signOut().catch(() => {});
    }
    clearTokens();
    setError(null);
  }, [clearTokens]);

  const clearError = useCallback(() => setError(null), []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        error,
        supabaseEnabled,
        login,
        register,
        signInWithOAuth,
        signInWithMagicLink,
        logout,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
