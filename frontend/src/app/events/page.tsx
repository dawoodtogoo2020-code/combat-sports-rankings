"use client";

import { useState } from "react";
import Link from "next/link";

const demoEvents = [
  { id: "1", name: "ADCC World Championships 2025", date: "2025-09-20", city: "Las Vegas", country: "US", tier: "elite", organizer: "ADCC", isGi: false, isNogi: true, matchCount: 248 },
  { id: "2", name: "IBJJF World Championship 2025", date: "2025-06-01", city: "Anaheim", country: "US", tier: "elite", organizer: "IBJJF", isGi: true, isNogi: false, matchCount: 1200 },
  { id: "3", name: "AJP Abu Dhabi Grand Slam", date: "2025-04-15", city: "Abu Dhabi", country: "AE", tier: "international", organizer: "AJP", isGi: true, isNogi: true, matchCount: 680 },
  { id: "4", name: "Grappling Industries NYC", date: "2025-03-10", city: "New York", country: "US", tier: "regional", organizer: "Grappling Industries", isGi: true, isNogi: true, matchCount: 320 },
  { id: "5", name: "NAGA Chicago Open", date: "2025-02-22", city: "Chicago", country: "US", tier: "regional", organizer: "NAGA", isGi: true, isNogi: true, matchCount: 180 },
  { id: "6", name: "Polaris Invitational 25", date: "2025-05-18", city: "London", country: "GB", tier: "international", organizer: "Polaris", isGi: false, isNogi: true, matchCount: 16 },
];

const tierColors: Record<string, string> = {
  elite: "badge-gold",
  international: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  national: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
  regional: "bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300",
  local: "bg-slate-50 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
};

export default function EventsPage() {
  const [search, setSearch] = useState("");

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Events</h1>
          <p className="mt-1 text-slate-600 dark:text-slate-400">Competitions tracked for ELO rankings</p>
        </div>
        <input
          type="text"
          placeholder="Search events..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input w-full sm:w-72"
        />
      </div>

      <div className="space-y-4">
        {demoEvents
          .filter((e) => e.name.toLowerCase().includes(search.toLowerCase()))
          .map((event) => (
            <Link
              key={event.id}
              href={`/events/${event.id}`}
              className="card group block transition-shadow hover:shadow-md"
            >
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="text-lg font-semibold text-slate-900 group-hover:text-brand-600 dark:text-white dark:group-hover:text-brand-400">
                      {event.name}
                    </h3>
                    <span className={`badge ${tierColors[event.tier]}`}>
                      {event.tier.toUpperCase()}
                    </span>
                  </div>
                  <div className="mt-1 flex flex-wrap items-center gap-3 text-sm text-slate-500 dark:text-slate-400">
                    <span>{new Date(event.date).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}</span>
                    <span>&middot;</span>
                    <span>{event.city}, {event.country}</span>
                    <span>&middot;</span>
                    <span>{event.organizer}</span>
                  </div>
                </div>
                <div className="flex items-center gap-4 text-sm">
                  <div className="flex gap-1">
                    {event.isGi && <span className="badge bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300">Gi</span>}
                    {event.isNogi && <span className="badge bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300">No-Gi</span>}
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-slate-900 dark:text-white">{event.matchCount}</div>
                    <div className="text-xs text-slate-500">matches</div>
                  </div>
                </div>
              </div>
            </Link>
          ))}
      </div>
    </div>
  );
}
