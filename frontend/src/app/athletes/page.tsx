"use client";

import { useState } from "react";
import Link from "next/link";

const demoAthletes = [
  { id: "1", name: "Gordon Ryan", country: "United States", countryCode: "US", gender: "male", rating: 2145, matches: 48, wins: 42, losses: 6, belt: "Black", verified: true },
  { id: "2", name: "Andre Galvao", country: "Brazil", countryCode: "BR", gender: "male", rating: 2098, matches: 62, wins: 54, losses: 8, belt: "Black", verified: true },
  { id: "3", name: "Gabi Garcia", country: "Brazil", countryCode: "BR", gender: "female", rating: 1920, matches: 45, wins: 40, losses: 5, belt: "Black", verified: true },
  { id: "4", name: "Felipe Pena", country: "Brazil", countryCode: "BR", gender: "male", rating: 2067, matches: 55, wins: 47, losses: 8, belt: "Black", verified: true },
  { id: "5", name: "Beatriz Mesquita", country: "Brazil", countryCode: "BR", gender: "female", rating: 1890, matches: 50, wins: 44, losses: 6, belt: "Black", verified: true },
  { id: "6", name: "Nicholas Meregali", country: "Brazil", countryCode: "BR", gender: "male", rating: 2034, matches: 41, wins: 36, losses: 5, belt: "Black", verified: true },
];

export default function AthletesPage() {
  const [search, setSearch] = useState("");

  const filtered = demoAthletes.filter((a) =>
    a.name.toLowerCase().includes(search.toLowerCase())
  );

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

      {filtered.length === 0 ? (
        <div className="card py-16 text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-surface-100 dark:bg-surface-800">
            <svg className="h-8 w-8 text-surface-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <h3 className="mt-4 text-lg font-semibold text-surface-900 dark:text-white">No athletes found</h3>
          <p className="mt-2 text-sm text-surface-500 dark:text-surface-400">
            Try adjusting your search to find what you&apos;re looking for.
          </p>
        </div>
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
                    {athlete.name[0]}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-surface-900 transition-colors group-hover:text-primary-600 dark:text-white dark:group-hover:text-primary-400">
                        {athlete.name}
                      </h3>
                      {athlete.verified && (
                        <svg className="h-4 w-4 text-primary-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      )}
                    </div>
                    <p className="text-sm text-surface-500 dark:text-surface-400">
                      {athlete.country} &middot; {athlete.belt} Belt
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-4 grid grid-cols-3 gap-4 border-t border-surface-100 pt-4 dark:border-surface-700/50">
                <div className="text-center">
                  <div className="font-mono text-lg font-bold text-primary-600 dark:text-primary-400">
                    {athlete.rating}
                  </div>
                  <div className="text-xs text-surface-500 dark:text-surface-400">ELO</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-surface-900 dark:text-white">
                    {athlete.matches}
                  </div>
                  <div className="text-xs text-surface-500 dark:text-surface-400">Matches</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-moss-600 dark:text-moss-400">
                    {Math.round((athlete.wins / athlete.matches) * 100)}%
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
