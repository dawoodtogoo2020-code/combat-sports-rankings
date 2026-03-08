"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import { useApi } from "@/hooks/useApi";
import { athletes as athletesApi } from "@/lib/api";
import type { AthleteListItem } from "@/types/index";
import { SkeletonCard } from "@/components/ui/Skeleton";
import { EmptyState, AthletesIcon } from "@/components/ui/EmptyState";

export default function AthletesPage() {
  const [search, setSearch] = useState("");
  const { data, loading } = useApi<AthleteListItem[]>(
    () => athletesApi.list() as Promise<AthleteListItem[]>,
    []
  );

  const filtered = useMemo(() => {
    if (!data) return [];
    if (!search) return data;
    return data.filter((a) =>
      a.display_name.toLowerCase().includes(search.toLowerCase())
    );
  }, [data, search]);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-surface-900 dark:text-white">Athletes</h1>
          <p className="mt-1 text-surface-500 dark:text-surface-400">Browse ranked combat sports athletes</p>
        </div>
        <input
          type="text"
          placeholder="Search athletes..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input w-full sm:w-72"
        />
      </div>

      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={<AthletesIcon />}
          title={search ? "No athletes found" : "No athletes yet"}
          description={
            search
              ? "Try adjusting your search to find what you\u2019re looking for."
              : "Athletes will appear here once competition data is imported."
          }
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((athlete) => (
            <Link
              key={athlete.id}
              href={`/athletes/${athlete.id}`}
              className="card-hover group"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary-50 text-lg font-bold text-primary-600 dark:bg-primary-950/40 dark:text-primary-400">
                    {athlete.display_name[0]}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-surface-900 transition-colors group-hover:text-primary-600 dark:text-white dark:group-hover:text-primary-400">
                        {athlete.display_name}
                      </h3>
                      {athlete.is_verified && (
                        <svg className="h-4 w-4 text-primary-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      )}
                    </div>
                    <p className="text-sm text-surface-500 dark:text-surface-400">
                      {athlete.country || "Unknown"}
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-4 grid grid-cols-3 gap-4 border-t border-surface-100 pt-4 dark:border-surface-700/50">
                <div className="text-center">
                  <div className="font-mono text-lg font-bold text-primary-600 dark:text-primary-400">
                    {athlete.elo_rating}
                  </div>
                  <div className="text-xs text-surface-500 dark:text-surface-400">ELO</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-surface-900 dark:text-white">
                    {athlete.total_matches}
                  </div>
                  <div className="text-xs text-surface-500 dark:text-surface-400">Matches</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-moss-600 dark:text-moss-400">
                    {athlete.total_matches > 0 ? Math.round((athlete.wins / athlete.total_matches) * 100) : 0}%
                  </div>
                  <div className="text-xs text-surface-500 dark:text-surface-400">Win Rate</div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
