"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/auth/AuthProvider";

export default function AuthPage() {
  const { login, register, error: authError, isLoading, clearError } = useAuth();
  const router = useRouter();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");
  const [fullName, setFullName] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const validate = () => {
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setFormError("Please enter a valid email address");
      return false;
    }
    if (password.length < 8) {
      setFormError("Password must be at least 8 characters");
      return false;
    }
    if (!isLogin && !username.trim()) {
      setFormError("Username is required");
      return false;
    }
    if (!isLogin && !fullName.trim()) {
      setFormError("Full name is required");
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    clearError();

    if (!validate()) return;

    setSubmitting(true);
    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await register({ email, username, password, full_name: fullName });
      }
      router.push("/");
    } catch {
      // Error is set via authError from context
    } finally {
      setSubmitting(false);
    }
  };

  const displayError = formError || authError;

  return (
    <div className="relative flex min-h-[calc(100vh-4rem)] items-center justify-center px-4 py-12">
      {/* Atmospheric background */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-950/20 via-transparent to-accent-950/10 dark:from-primary-950/40 dark:to-accent-950/20" />
        <div className="absolute left-1/4 top-1/3 h-96 w-96 rounded-full bg-primary-500/5 blur-3xl dark:bg-primary-500/10" />
        <div className="absolute bottom-1/4 right-1/4 h-64 w-64 rounded-full bg-accent-500/5 blur-3xl dark:bg-accent-500/8" />
      </div>

      <div className="relative w-full max-w-md">
        <div className="text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-600 to-primary-800 text-lg font-bold text-white shadow-glow">
            CS
          </div>
          <h1 className="mt-5 text-2xl font-bold text-surface-900 dark:text-white">
            {isLogin ? "Sign in to CS Rankings" : "Create your account"}
          </h1>
          <p className="mt-2 text-sm text-surface-500 dark:text-surface-400">
            {isLogin
              ? "Track your combat sports ranking"
              : "Join the global combat sports community"}
          </p>
        </div>

        <div className="card mt-8">
          {displayError && (
            <div className="mb-4 rounded-xl border border-clay-200 bg-clay-50 px-4 py-3 text-sm text-clay-700 dark:border-clay-800/50 dark:bg-clay-900/20 dark:text-clay-400">
              {displayError}
            </div>
          )}

          <form className="space-y-5" onSubmit={handleSubmit}>
            {!isLogin && (
              <>
                <div>
                  <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="input mt-1.5 w-full"
                    placeholder="John Doe"
                    autoComplete="name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">
                    Username
                  </label>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="input mt-1.5 w-full"
                    placeholder="johndoe"
                    autoComplete="username"
                  />
                </div>
              </>
            )}

            <div>
              <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input mt-1.5 w-full"
                placeholder="you@example.com"
                autoComplete="email"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">
                Password
              </label>
              <div className="relative mt-1.5">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input w-full pr-10"
                  placeholder="Min. 8 characters"
                  autoComplete={isLogin ? "current-password" : "new-password"}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-surface-400 hover:text-surface-600 dark:hover:text-surface-300"
                  tabIndex={-1}
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    {showPassword ? (
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    ) : (
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    )}
                  </svg>
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="btn-primary w-full py-2.5 shadow-glow disabled:opacity-60"
            >
              {submitting ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  {isLogin ? "Signing in..." : "Creating account..."}
                </span>
              ) : (
                isLogin ? "Sign In" : "Create Account"
              )}
            </button>
          </form>

          <div className="mt-5 text-center">
            <button
              onClick={() => {
                setIsLogin(!isLogin);
                setFormError(null);
                clearError();
              }}
              className="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 transition-colors"
            >
              {isLogin ? "Don\u2019t have an account? Sign up" : "Already have an account? Sign in"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
