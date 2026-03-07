"use client";

import { useState } from "react";
import Link from "next/link";

const demoGyms = [
  { id: "1", name: "New Wave Jiu-Jitsu", city: "Austin", country: "US", members: 45, avgRating: 1680, verified: true, style: "No-Gi" },
  { id: "2", name: "Atos Jiu-Jitsu", city: "San Diego", country: "US", members: 120, avgRating: 1620, verified: true, style: "Both" },
  { id: "3", name: "Alliance BJJ", city: "Atlanta", country: "US", members: 200, avgRating: 1590, verified: true, style: "Both" },
  { id: "4", name: "Gracie Barra HQ", city: "Rio de Janeiro", country: "BR", members: 180, avgRating: 1570, verified: true, style: "Gi" },
  { id: "5", name: "Renzo Gracie Academy", city: "New York", country: "US", members: 150, avgRating: 1560, verified: true, style: "Both" },
  { id: "6", name: "Dream Art BJJ", city: "Sao Paulo", country: "BR", members: 80, avgRating: 1640, verified: true, style: "Gi" },
];

export default function GymsPage() {
  const [search, setSearch] = useState("");

  const filtered = demoGyms.filter((g) =>
    g.name.toLowerCase().includes(search.toLowerCase())
  );

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

      {filtered.length > 0 ? (
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
                    {gym.verified && (
                      <svg className="h-4 w-4 flex-shrink-0 text-primary-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                  <p className="text-sm text-surface-500 dark:text-surface-400">
                    {gym.city}, {gym.country}
                  </p>
                </div>
              </div>

              <div className="mt-4 flex items-center gap-2">
                <span className="badge bg-surface-100 text-surface-600 dark:bg-surface-800 dark:text-surface-300">
                  {gym.style}
                </span>
              </div>

              <div className="mt-4 grid grid-cols-2 gap-4 border-t border-surface-100 pt-4 dark:border-surface-700/30">
                <div className="text-center">
                  <div className="text-lg font-bold text-surface-900 dark:text-white">{gym.members}</div>
                  <div className="text-xs text-surface-500 dark:text-surface-400">Members</div>
                </div>
                <div className="text-center">
                  <div className="font-mono text-lg font-bold text-primary-600 dark:text-primary-400">{gym.avgRating}</div>
                  <div className="text-xs text-surface-500 dark:text-surface-400">Avg Rating</div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="card py-16 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-surface-100 dark:bg-surface-800">
            <svg className="h-8 w-8 text-surface-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-surface-900 dark:text-white">No gyms found</h3>
          <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">
            Try adjusting your search terms
          </p>
        </div>
      )}
    </div>
  );
}
