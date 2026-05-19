"use client";

import { useEffect } from "react";

const DSN = process.env.NEXT_PUBLIC_SENTRY_DSN;
const ENV = process.env.NEXT_PUBLIC_SENTRY_ENV ?? "production";

let initialized = false;

export function SentryInit() {
  useEffect(() => {
    if (initialized || !DSN) return;
    initialized = true;
    import("@sentry/nextjs")
      .then((Sentry) => {
        Sentry.init({
          dsn: DSN,
          environment: ENV,
          tracesSampleRate: 0.1,
          replaysSessionSampleRate: 0,
          replaysOnErrorSampleRate: 1.0,
        });
      })
      .catch(() => {
        // Sentry package not installed yet — fail silently in dev
      });
  }, []);

  return null;
}
