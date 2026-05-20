"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/auth/AuthProvider";

export default function AuthPage() {
  const {
    login,
    register,
    signInWithOAuth,
    signInWithMagicLink,
    supabaseEnabled,
    error: authError,
    isLoading,
    clearError,
  } = useAuth();
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register" | "magic">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");
  const [fullName, setFullName] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [magicSent, setMagicSent] = useState(false);
  const [oauthLoading, setOauthLoading] = useState<"google" | "github" | null>(null);

  const isLogin = mode === "login";
  const isRegister = mode === "register";
  const isMagic = mode === "magic";

  const validate = () => {
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setFormError("Please enter a valid email address");
      return false;
    }
    if (!isMagic && password.length < 8) {
      setFormError("Password must be at least 8 characters");
      return false;
    }
    if (isRegister && !username.trim()) {
      setFormError("Username is required");
      return false;
    }
    if (isRegister && !fullName.trim()) {
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
      if (isMagic) {
        await signInWithMagicLink(email);
        setMagicSent(true);
      } else if (isLogin) {
        await login(email, password);
        router.push("/");
      } else {
        await register({ email, username, password, full_name: fullName });
        router.push("/");
      }
    } catch {
      // Error is set via authError from context
    } finally {
      setSubmitting(false);
    }
  };

  const handleOAuth = async (provider: "google" | "github") => {
    setFormError(null);
    clearError();
    setOauthLoading(provider);
    try {
      await signInWithOAuth(provider);
      // Redirects away; no need to clear loading
    } catch {
      setOauthLoading(null);
    }
  };

  const displayError = formError || authError;

  return (
    <div className="relative flex min-h-[calc(100vh-4rem)] items-center justify-center px-4 py-12">
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
            {isLogin ? "Sign in to CS Rankings" : isRegister ? "Create your account" : "Sign in with email"}
          </h1>
          <p className="mt-2 text-sm text-surface-500 dark:text-surface-400">
            {isRegister ? "Join the global combat sports community" : "Track your combat sports ranking"}
          </p>
        </div>

        <div className="card mt-8">
          {displayError && (
            <div className="mb-4 rounded-xl border border-clay-200 bg-clay-50 px-4 py-3 text-sm text-clay-700 dark:border-clay-800/50 dark:bg-clay-900/20 dark:text-clay-400">
              {displayError}
            </div>
          )}

          {magicSent && isMagic && (
            <div className="mb-4 rounded-xl border border-moss-200 bg-moss-50 px-4 py-3 text-sm text-moss-800 dark:border-moss-800/50 dark:bg-moss-900/20 dark:text-moss-300">
              Check your inbox for a sign-in link.
            </div>
          )}

          {supabaseEnabled && !isMagic && (
            <>
              <div className="space-y-2">
                <button
                  type="button"
                  onClick={() => handleOAuth("google")}
                  disabled={oauthLoading !== null}
                  className="flex w-full items-center justify-center gap-3 rounded-xl border border-surface-300 bg-white py-2.5 text-sm font-medium text-surface-800 transition hover:bg-surface-50 disabled:opacity-60 dark:border-surface-700 dark:bg-surface-900 dark:text-surface-100 dark:hover:bg-surface-800"
                >
                  <svg className="h-4 w-4" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84A10.99 10.99 0 0012 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18a11 11 0 000 9.86l3.66-2.84z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84C6.71 7.31 9.14 5.38 12 5.38z"/>
                  </svg>
                  {oauthLoading === "google" ? "Redirecting..." : "Continue with Google"}
                </button>
                <button
                  type="button"
                  onClick={() => handleOAuth("github")}
                  disabled={oauthLoading !== null}
                  className="flex w-full items-center justify-center gap-3 rounded-xl border border-surface-300 bg-white py-2.5 text-sm font-medium text-surface-800 transition hover:bg-surface-50 disabled:opacity-60 dark:border-surface-700 dark:bg-surface-900 dark:text-surface-100 dark:hover:bg-surface-800"
                >
                  <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.1.79-.25.79-.55v-2.04c-3.2.7-3.88-1.36-3.88-1.36-.52-1.33-1.27-1.69-1.27-1.69-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.18 1.76 1.18 1.02 1.75 2.68 1.24 3.34.95.1-.74.4-1.24.72-1.53-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.29 1.18-3.1-.12-.29-.51-1.47.11-3.06 0 0 .97-.31 3.18 1.18.92-.26 1.91-.39 2.9-.39s1.98.13 2.9.39c2.21-1.49 3.18-1.18 3.18-1.18.62 1.59.23 2.77.11 3.06.74.81 1.18 1.84 1.18 3.1 0 4.42-2.69 5.39-5.25 5.68.41.36.78 1.05.78 2.12v3.14c0 .31.21.66.79.55C20.21 21.39 23.5 17.08 23.5 12 23.5 5.65 18.35.5 12 .5z"/>
                  </svg>
                  {oauthLoading === "github" ? "Redirecting..." : "Continue with GitHub"}
                </button>
                <button
                  type="button"
                  onClick={() => { setMode("magic"); setFormError(null); clearError(); setMagicSent(false); }}
                  className="flex w-full items-center justify-center gap-2 rounded-xl border border-surface-300 bg-white py-2.5 text-sm font-medium text-surface-800 transition hover:bg-surface-50 dark:border-surface-700 dark:bg-surface-900 dark:text-surface-100 dark:hover:bg-surface-800"
                >
                  Email me a sign-in link
                </button>
              </div>

              <div className="my-5 flex items-center gap-3 text-xs uppercase tracking-wider text-surface-400 dark:text-surface-500">
                <span className="h-px flex-1 bg-surface-200 dark:bg-surface-800" />
                or
                <span className="h-px flex-1 bg-surface-200 dark:bg-surface-800" />
              </div>
            </>
          )}

          <form className="space-y-5" onSubmit={handleSubmit}>
            {isRegister && (
              <>
                <div>
                  <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Full Name</label>
                  <input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} className="input mt-1.5 w-full" placeholder="John Doe" autoComplete="name" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Username</label>
                  <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} className="input mt-1.5 w-full" placeholder="johndoe" autoComplete="username" />
                </div>
              </>
            )}

            <div>
              <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Email</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="input mt-1.5 w-full" placeholder="you@example.com" autoComplete="email" />
            </div>

            {!isMagic && (
              <div>
                <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Password</label>
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
            )}

            <button type="submit" disabled={submitting || isLoading} className="btn-primary w-full py-2.5 shadow-glow disabled:opacity-60">
              {submitting ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  {isMagic ? "Sending link..." : isLogin ? "Signing in..." : "Creating account..."}
                </span>
              ) : (
                isMagic ? "Send sign-in link" : isLogin ? "Sign In" : "Create Account"
              )}
            </button>
          </form>

          <div className="mt-5 flex flex-col gap-1 text-center text-sm">
            {!isMagic ? (
              <button
                onClick={() => { setMode(isLogin ? "register" : "login"); setFormError(null); clearError(); }}
                className="text-primary-600 hover:text-primary-700 transition-colors dark:text-primary-400 dark:hover:text-primary-300"
              >
                {isLogin ? "Don’t have an account? Sign up" : "Already have an account? Sign in"}
              </button>
            ) : (
              <button
                onClick={() => { setMode("login"); setFormError(null); clearError(); setMagicSent(false); }}
                className="text-primary-600 hover:text-primary-700 transition-colors dark:text-primary-400 dark:hover:text-primary-300"
              >
                Back to password sign-in
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
