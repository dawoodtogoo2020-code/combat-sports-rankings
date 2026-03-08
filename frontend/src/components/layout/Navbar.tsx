"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import { useTheme } from "./ThemeProvider";
import { useAuth } from "@/components/auth/AuthProvider";
import { LogoMark } from "@/components/ui/Logo";

const navLinks = [
  { href: "/", label: "Home" },
  { href: "/athletes", label: "Athletes" },
  { href: "/leaderboards", label: "Leaderboards" },
  { href: "/events", label: "Events" },
  { href: "/gyms", label: "Gyms" },
  { href: "/social", label: "Social" },
];

export function Navbar() {
  const { theme, toggleTheme } = useTheme();
  const { user, logout, isLoading: authLoading } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    setMobileOpen(false);
    setUserMenuOpen(false);
  }, [pathname]);

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  return (
    <header className="sticky top-0 z-50 border-b border-surface-200/50 bg-white/80 backdrop-blur-xl dark:border-surface-700/30 dark:bg-surface-900/80">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5">
          <div className="text-primary-600 dark:text-primary-400">
            <LogoMark className="h-8 w-8" />
          </div>
          <span className="text-lg font-bold tracking-tight text-surface-900 dark:text-white">
            Rankings
          </span>
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden items-center gap-0.5 md:flex">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`relative rounded-xl px-3.5 py-2 text-sm font-medium transition-colors ${
                isActive(link.href)
                  ? "text-primary-700 dark:text-primary-300"
                  : "text-surface-500 hover:text-surface-900 dark:text-surface-400 dark:hover:text-white"
              }`}
            >
              {link.label}
              {isActive(link.href) && (
                <span className="absolute bottom-0 left-1/2 h-0.5 w-5 -translate-x-1/2 rounded-full bg-primary-500/70" />
              )}
            </Link>
          ))}
        </nav>

        {/* Right Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={toggleTheme}
            className="rounded-xl p-2 text-surface-500 transition-colors hover:bg-surface-100 hover:text-surface-700 dark:text-surface-400 dark:hover:bg-surface-800 dark:hover:text-surface-200"
            aria-label="Toggle theme"
          >
            {theme === "dark" ? (
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            ) : (
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            )}
          </button>

          {/* Auth state — desktop */}
          {!authLoading && (
            <>
              {user ? (
                <div className="relative hidden sm:block">
                  <button
                    onClick={() => setUserMenuOpen(!userMenuOpen)}
                    className="flex items-center gap-2 rounded-xl px-3 py-1.5 text-sm font-medium text-surface-700 transition-colors hover:bg-surface-100 dark:text-surface-300 dark:hover:bg-surface-800"
                  >
                    <div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary-100 text-xs font-bold text-primary-700 dark:bg-primary-900/40 dark:text-primary-300">
                      {user.full_name?.[0]?.toUpperCase() || user.username?.[0]?.toUpperCase() || "U"}
                    </div>
                    <span className="max-w-[100px] truncate">{user.full_name || user.username}</span>
                  </button>
                  {userMenuOpen && (
                    <>
                      <div className="fixed inset-0 z-40" onClick={() => setUserMenuOpen(false)} />
                      <div className="absolute right-0 z-50 mt-1 w-48 rounded-xl border border-surface-200/60 bg-white p-1 shadow-soft-lg dark:border-surface-700/40 dark:bg-surface-800">
                        <div className="border-b border-surface-100 px-3 py-2 dark:border-surface-700/50">
                          <div className="text-xs text-surface-400">{user.email}</div>
                          <div className="mt-0.5 text-xs font-medium capitalize text-surface-500">{user.role}</div>
                        </div>
                        {user.role === "admin" && (
                          <Link
                            href="/admin"
                            className="block rounded-lg px-3 py-2 text-sm text-surface-600 transition-colors hover:bg-surface-50 dark:text-surface-400 dark:hover:bg-surface-700"
                          >
                            Admin Panel
                          </Link>
                        )}
                        <button
                          onClick={() => { logout(); setUserMenuOpen(false); }}
                          className="w-full rounded-lg px-3 py-2 text-left text-sm text-clay-600 transition-colors hover:bg-clay-50 dark:text-clay-400 dark:hover:bg-clay-900/20"
                        >
                          Sign Out
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ) : (
                <Link href="/auth" className="btn-primary hidden text-sm sm:inline-flex">
                  Sign In
                </Link>
              )}
            </>
          )}

          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="rounded-xl p-2 text-surface-500 hover:bg-surface-100 dark:text-surface-400 dark:hover:bg-surface-800 md:hidden"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              {mobileOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile Nav */}
      <div
        className={`fixed inset-0 top-16 z-40 transition-all duration-300 md:hidden ${
          mobileOpen ? "pointer-events-auto opacity-100" : "pointer-events-none opacity-0"
        }`}
      >
        <div className="absolute inset-0 bg-black/20 backdrop-blur-sm" onClick={() => setMobileOpen(false)} />
        <nav className={`relative border-b border-surface-200/50 bg-white px-4 py-4 shadow-soft-lg transition-transform duration-300 dark:border-surface-700/30 dark:bg-surface-900 ${
          mobileOpen ? "translate-y-0" : "-translate-y-4"
        }`}>
          <div className="space-y-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`block rounded-xl px-4 py-2.5 text-sm font-medium transition-colors ${
                  isActive(link.href)
                    ? "bg-primary-50 text-primary-700 dark:bg-primary-950/30 dark:text-primary-300"
                    : "text-surface-600 hover:bg-surface-50 dark:text-surface-400 dark:hover:bg-surface-800"
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>
          <div className="mt-3 border-t border-surface-100 pt-3 dark:border-surface-700/50">
            {user ? (
              <div className="space-y-1">
                <div className="flex items-center gap-2 px-4 py-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-100 text-xs font-bold text-primary-700 dark:bg-primary-900/40 dark:text-primary-300">
                    {user.full_name?.[0]?.toUpperCase() || "U"}
                  </div>
                  <div>
                    <div className="text-sm font-medium text-surface-900 dark:text-white">{user.full_name || user.username}</div>
                    <div className="text-xs text-surface-400">{user.email}</div>
                  </div>
                </div>
                {user.role === "admin" && (
                  <Link href="/admin" className="block rounded-xl px-4 py-2.5 text-sm font-medium text-surface-600 hover:bg-surface-50 dark:text-surface-400 dark:hover:bg-surface-800">
                    Admin Panel
                  </Link>
                )}
                <button
                  onClick={() => { logout(); setMobileOpen(false); }}
                  className="w-full rounded-xl px-4 py-2.5 text-left text-sm font-medium text-clay-600 hover:bg-clay-50 dark:text-clay-400 dark:hover:bg-clay-900/20"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <Link href="/auth" className="btn-primary w-full justify-center py-2.5 text-sm">
                Sign In
              </Link>
            )}
          </div>
        </nav>
      </div>
    </header>
  );
}
