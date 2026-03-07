"use client";

import { useState } from "react";

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");
  const [fullName, setFullName] = useState("");

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
          <form className="space-y-5" onSubmit={(e) => e.preventDefault()}>
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
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input mt-1.5 w-full"
                placeholder="Min. 8 characters"
              />
              {isLogin && (
                <div className="mt-1.5 text-right">
                  <button type="button" className="text-xs text-surface-500 hover:text-primary-600 dark:text-surface-400 dark:hover:text-primary-400 transition-colors">
                    Forgot password?
                  </button>
                </div>
              )}
            </div>

            <button type="submit" className="btn-primary w-full py-2.5 shadow-glow">
              {isLogin ? "Sign In" : "Create Account"}
            </button>
          </form>

          <div className="mt-5 text-center">
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 transition-colors"
            >
              {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
