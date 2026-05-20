"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/auth/AuthProvider";

/**
 * OAuth + magic-link landing page. Supabase appends the session to the URL
 * fragment; the AuthProvider bootstrap effect detects it via getSession()
 * and exchanges it for our JWT. We just wait for `user` to populate, then
 * redirect home.
 */
export default function AuthCallbackPage() {
  const { user, isLoading, error } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && user) {
      router.replace("/");
    }
  }, [user, isLoading, router]);

  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center px-4">
      <div className="card max-w-md text-center">
        {error ? (
          <>
            <h1 className="text-xl font-semibold text-clay-700 dark:text-clay-400">Sign-in failed</h1>
            <p className="mt-2 text-sm text-surface-500 dark:text-surface-400">{error}</p>
            <button
              onClick={() => router.replace("/auth")}
              className="btn-primary mt-6"
            >
              Try again
            </button>
          </>
        ) : (
          <>
            <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
            <h1 className="mt-4 text-lg font-medium text-surface-800 dark:text-surface-100">
              Finishing sign-in…
            </h1>
            <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">
              Almost there.
            </p>
          </>
        )}
      </div>
    </div>
  );
}
