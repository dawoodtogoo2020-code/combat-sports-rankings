"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import { useApi } from "@/hooks/useApi";
import { events as eventsApi } from "@/lib/api";
import type { Event } from "@/types/index";
import { SkeletonCard } from "@/components/ui/Skeleton";
import { EmptyState, EventsIcon } from "@/components/ui/EmptyState";

const tierStyles: Record<string, string> = {
  elite: "badge-gold",
  international: "bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400",
  national: "bg-accent-100 text-accent-700 dark:bg-accent-900/30 dark:text-accent-400",
  regional: "bg-surface-200 text-surface-600 dark:bg-surface-700 dark:text-surface-300",
  local: "bg-surface-100 text-surface-500 dark:bg-surface-800 dark:text-surface-400",
};

export default function EventsPage() {
  const [search, setSearch] = useState("");
  const { data, loading } = useApi<Event[]>(
    () => eventsApi.list() as Promise<Event[]>,
    []
  );

  const filtered = useMemo(() => {
    if (!data) return [];
    if (!search) return data;
    return data.filter((e) =>
      e.name.toLowerCase().includes(search.toLowerCase())
    );
  }, [data, search]);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-surface-900 dark:text-white">Events</h1>
          <p className="mt-1 text-surface-500 dark:text-surface-400">Competitions and tournaments</p>
        </div>
        <input
          type="text"
          placeholder="Search events..."
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
          icon={<EventsIcon />}
          title={search ? "No events found" : "No events yet"}
          description={
            search
              ? "Try adjusting your search."
              : "Events will appear here once competition data is imported."
          }
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((event) => (
            <Link
              key={event.id}
              href={`/events/${event.id}`}
              className="card-hover group"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="truncate font-semibold text-surface-900 transition-colors group-hover:text-primary-600 dark:text-white dark:group-hover:text-primary-400">
                    {event.name}
                  </h3>
                  <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">
                    {event.city ? `${event.city}, ` : ""}{event.country || "TBD"}
                  </p>
                </div>
                <span className={`badge ml-2 flex-shrink-0 ${tierStyles[event.tier] || tierStyles.local}`}>
                  {event.tier}
                </span>
              </div>
              <div className="mt-3 text-xs text-surface-400 dark:text-surface-500">
                {new Date(event.event_date).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
                {event.organizer && ` \u00b7 ${event.organizer}`}
              </div>
              <div className="mt-3 flex gap-1.5">
                {event.is_gi && <span className="badge bg-surface-100 text-surface-600 dark:bg-surface-700 dark:text-surface-300">Gi</span>}
                {event.is_nogi && <span className="badge bg-surface-100 text-surface-600 dark:bg-surface-700 dark:text-surface-300">No-Gi</span>}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
