"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { useApi } from "@/hooks/useApi";
import { gyms as gymsApi } from "@/lib/api";
import type { Gym, AthleteListItem } from "@/types/index";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState, GymsIcon } from "@/components/ui/EmptyState";

export default function GymDetailClient() {
  const params = useParams();
  const id = params?.id as string;

  const { data: gym, loading } = useApi<Gym>(
    () => gymsApi.get(id) as Promise<Gym>,
    [id]
  );
  const { data: gymAthletes } = useApi<AthleteListItem[]>(
    () => gymsApi.athletes(id) as Promise<AthleteListItem[]>,
    [id]
  );

  if (loading) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        <Skeleton className="mb-6 h-4 w-24" />
        <div className="card mb-6 space-y-4">
          <div className="flex gap-6">
            <Skeleton className="h-20 w-20 rounded-2xl" />
            <div className="flex-1 space-y-3">
              <Skeleton className="h-7 w-48" />
              <Skeleton className="h-4 w-32" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!gym) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        <EmptyState
          icon={<GymsIcon />}
          title="Gym not found"
          description="This gym doesn't exist or hasn't been registered yet."
          actionLabel="Browse Gyms"
          actionHref="/gyms"
        />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <div className="mb-6">
        <Link href="/gyms" className="text-sm text-surface-500 hover:text-primary-600 dark:text-surface-400 dark:hover:text-primary-400 transition-colors">
          &larr; Back to Gyms
        </Link>
      </div>

      {/* Header Card */}
      <div className="card mb-6">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-start">
          <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-primary-50 text-3xl font-bold text-primary-600 dark:bg-primary-950/40 dark:text-primary-400">
            {gym.name.substring(0, 2).toUpperCase()}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-surface-900 dark:text-white">{gym.name}</h1>
              {gym.is_verified && (
                <svg className="h-5 w-5 text-primary-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              )}
            </div>
            <p className="mt-1 text-surface-500 dark:text-surface-400">
              {gym.city && `${gym.city}, `}{gym.country || "Unknown"}
            </p>
            {gym.description && (
              <p className="mt-3 text-sm text-surface-600 dark:text-surface-300">
                {gym.description}
              </p>
            )}
          </div>
          <div className="flex gap-8 text-center sm:flex-col sm:gap-4">
            <div>
              <div className="text-2xl font-bold text-surface-900 dark:text-white">{gym.member_count}</div>
              <div className="text-xs text-surface-500 dark:text-surface-400">Members</div>
            </div>
            <div>
              <div className="font-mono text-2xl font-bold text-primary-600 dark:text-primary-400">{gym.avg_rating}</div>
              <div className="text-xs text-surface-500 dark:text-surface-400">Avg Rating</div>
            </div>
          </div>
        </div>
      </div>

      {/* Top Athletes */}
      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-white">Athletes</h2>
        {!gymAthletes || gymAthletes.length === 0 ? (
          <div className="py-8 text-center text-sm text-surface-400">
            No athletes are linked to this gym yet.
          </div>
        ) : (
          <div className="space-y-3">
            {gymAthletes.map((a, i) => (
              <Link
                key={a.id}
                href={`/athletes/${a.id}`}
                className="flex items-center justify-between rounded-xl border border-surface-100 p-4 transition-colors hover:bg-surface-50 dark:border-surface-700/30 dark:hover:bg-surface-850/50"
              >
                <div className="flex items-center gap-3">
                  <span
                    className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold ${
                      i === 0
                        ? "bg-gold-100 text-gold-700 dark:bg-gold-900/30 dark:text-gold-400"
                        : i === 1
                        ? "bg-surface-200 text-surface-600 dark:bg-surface-700 dark:text-surface-300"
                        : i === 2
                        ? "bg-gold-100/60 text-gold-700 dark:bg-gold-900/20 dark:text-gold-500"
                        : "text-surface-500 dark:text-surface-400"
                    }`}
                  >
                    {i + 1}
                  </span>
                  <span className="font-medium text-surface-900 dark:text-white">{a.display_name}</span>
                </div>
                <div className="flex items-center gap-5 text-sm">
                  <span className="text-surface-500 dark:text-surface-400">{a.wins}-{a.losses}</span>
                  <span className="font-mono font-bold text-primary-600 dark:text-primary-400">{a.elo_rating}</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
