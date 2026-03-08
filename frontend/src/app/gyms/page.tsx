"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import { useApi } from "@/hooks/useApi";
import { gyms as gymsApi } from "@/lib/api";
import type { Gym } from "@/types/index";
import { SkeletonCard } from "@/components/ui/Skeleton";
import { EmptyState, GymsIcon } from "@/components/ui/EmptyState";

export default function GymsPage() {
  const [search, setSearch] = useState("");
  const { data, loading } = useApi<Gym[]>(
    () => gymsApi.list() as Promise<Gym[]>,
    []
  );

  const filtered = useMemo(() => {
    if (!data) return [];
    if (!search) return data;
    return data.filter((g) =>
      g.name.toLowerCase().includes(search.toLowerCase())
    );
  }, [data, search]);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-surface-900 dark:text-white">Gyms</h1>
          <p className="mt-1 text-surface-500 dark:text-surface-400">
            Combat sports academies and training centers
          </p>
        </div>
        <input
          type="text"
          placeholder="Search gyms..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input w-full sm:w-72"
        />
      </div>

      {loading ? (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={<GymsIcon />}
          title={search ? "No gyms found" : "No gyms yet"}
          description={
            search
              ? "Try adjusting your search terms."
              : "Gyms will appear here once they register on the platform."
          }
        />
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((gym) => (
            <Link
              key={gym.id}
              href={`/gyms/${gym.id}`}
              className="card card-hover group"
            >
              <div className="flex items-start gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-50 text-lg font-bold text-primary-600 dark:bg-primary-950/40 dark:text-primary-400">
                  {gym.name[0]}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="truncate font-semibold text-surface-900 group-hover:text-primary-600 dark:text-white dark:group-hover:text-primary-400 transition-colors">
                      {gym.name}
                    </h3>
                    {gym.is_verified && (
                      <svg className="h-4 w-4 flex-shrink-0 text-primary-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                  <p className="text-sm text-surface-500 dark:text-surface-400">
                    {gym.city && `${gym.city}, `}{gym.country || "Unknown"}
                  </p>
                </div>
              </div>

              <div className="mt-4 grid grid-cols-2 gap-4 border-t border-surface-100 pt-4 dark:border-surface-700/30">
                <div className="text-center">
                  <div className="text-lg font-bold text-surface-900 dark:text-white">{gym.member_count}</div>
                  <div className="text-xs text-surface-500 dark:text-surface-400">Members</div>
                </div>
                <div className="text-center">
                  <div className="font-mono text-lg font-bold text-primary-600 dark:text-primary-400">{gym.avg_rating}</div>
                  <div className="text-xs text-surface-500 dark:text-surface-400">Avg Rating</div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
