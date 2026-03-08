"use client";

import { useState, useEffect, useCallback, useRef } from "react";

interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * Generic data-fetching hook with graceful error handling.
 * When the backend is unavailable, returns null data (not a crash).
 */
export function useApi<T>(
  fetcher: () => Promise<T>,
  deps: unknown[] = []
): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [trigger, setTrigger] = useState(0);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    fetcher()
      .then((result) => {
        if (!cancelled && mountedRef.current) {
          setData(result);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled && mountedRef.current) {
          // Network errors or backend unavailable — graceful empty state
          const msg = err instanceof Error ? err.message : "Failed to load data";
          setError(msg);
          setData(null);
          setLoading(false);
        }
      });

    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [trigger, ...deps]);

  const refetch = useCallback(() => setTrigger((t) => t + 1), []);

  return { data, loading, error, refetch };
}
