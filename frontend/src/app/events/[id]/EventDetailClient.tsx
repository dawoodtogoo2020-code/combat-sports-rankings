"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { useApi } from "@/hooks/useApi";
import { events as eventsApi } from "@/lib/api";
import type { Event, Match } from "@/types/index";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState, EventsIcon } from "@/components/ui/EmptyState";

export default function EventDetailClient() {
  const params = useParams();
  const id = params?.id as string;

  const { data: event, loading } = useApi<Event>(
    () => eventsApi.get(id) as Promise<Event>,
    [id]
  );
  const { data: matches } = useApi<Match[]>(
    () => eventsApi.matches(id) as Promise<Match[]>,
    [id]
  );

  if (loading) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        <div className="card mb-6 space-y-4">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-48" />
        </div>
      </div>
    );
  }

  if (!event) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        <EmptyState
          icon={<EventsIcon />}
          title="Event not found"
          description="This event doesn't exist or hasn't been imported yet."
          actionLabel="Browse Events"
          actionHref="/events"
        />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <div className="mb-6">
        <Link href="/events" className="text-sm text-surface-500 hover:text-primary-600 dark:text-surface-400 dark:hover:text-primary-400 transition-colors">
          &larr; Back to Events
        </Link>
      </div>

      {/* Event Header */}
      <div className="card mb-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-surface-900 dark:text-white">
                {event.name}
              </h1>
              <span className="badge badge-gold uppercase">{event.tier}</span>
            </div>
            <p className="mt-2 text-surface-500 dark:text-surface-400">
              {new Date(event.event_date).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}
              {event.city && ` \u00b7 ${event.city}`}
              {event.country && `, ${event.country}`}
              {event.organizer && ` \u00b7 ${event.organizer}`}
            </p>
          </div>
          <div className="flex gap-2">
            {event.is_gi && <span className="badge bg-surface-100 text-surface-600 dark:bg-surface-700 dark:text-surface-300">Gi</span>}
            {event.is_nogi && <span className="badge bg-surface-100 text-surface-600 dark:bg-surface-700 dark:text-surface-300">No-Gi</span>}
            {event.k_factor_multiplier > 1 && (
              <span className="badge bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400">
                {event.k_factor_multiplier}x K-Factor
              </span>
            )}
          </div>
        </div>
        {event.description && (
          <p className="mt-4 text-sm text-surface-600 dark:text-surface-400">{event.description}</p>
        )}
      </div>

      {/* Match Results */}
      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-white">Match Results</h2>
        {!matches || matches.length === 0 ? (
          <div className="py-8 text-center text-sm text-surface-400">
            No match results have been imported for this event yet.
          </div>
        ) : (
          <div className="space-y-3">
            {matches.map((m) => (
              <div key={m.id} className="flex items-center justify-between rounded-xl border border-surface-100 p-3.5 dark:border-surface-700/50">
                <div className="flex-1">
                  <div className="flex items-center gap-2 text-sm">
                    <Link href={`/athletes/${m.winner_id}`} className="font-semibold text-moss-600 hover:underline dark:text-moss-400">
                      {m.winner_name || "Winner"}
                    </Link>
                    <span className="text-surface-400">def.</span>
                    <Link href={`/athletes/${m.loser_id}`} className="text-surface-600 hover:underline dark:text-surface-300">
                      {m.loser_name || "Opponent"}
                    </Link>
                  </div>
                  <div className="mt-1 flex items-center gap-2 text-xs text-surface-400">
                    <span className="capitalize">{m.outcome}</span>
                    {m.submission_type && <span>({m.submission_type})</span>}
                    {m.round_name && <span className="text-surface-300 dark:text-surface-500">&middot; {m.round_name}</span>}
                    {m.is_gi ? <span className="text-surface-300 dark:text-surface-500">&middot; Gi</span> : <span className="text-surface-300 dark:text-surface-500">&middot; No-Gi</span>}
                  </div>
                </div>
                {m.elo_change != null && (
                  <span className={`font-mono text-sm font-medium ${m.elo_change > 0 ? "rating-up" : "rating-down"}`}>
                    {m.elo_change > 0 ? "+" : ""}{Math.round(m.elo_change)}
                  </span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
