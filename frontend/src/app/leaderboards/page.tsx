"use client";

import { useState } from "react";

// Demo data for rendering
const demoEntries = [
  { rank: 1, name: "Gordon Ryan", country: "US", rating: 2145, matches: 48, wins: 42, losses: 6, winRate: 87.5, change: "+12" },
  { rank: 2, name: "Andre Galvao", country: "BR", rating: 2098, matches: 62, wins: 54, losses: 8, winRate: 87.1, change: "+5" },
  { rank: 3, name: "Felipe Pena", country: "BR", rating: 2067, matches: 55, wins: 47, losses: 8, winRate: 85.5, change: "-3" },
  { rank: 4, name: "Nicholas Meregali", country: "BR", rating: 2034, matches: 41, wins: 36, losses: 5, winRate: 87.8, change: "+18" },
  { rank: 5, name: "Giancarlo Bodoni", country: "US", rating: 2012, matches: 35, wins: 30, losses: 5, winRate: 85.7, change: "+8" },
  { rank: 6, name: "Kaynan Duarte", country: "BR", rating: 1998, matches: 44, wins: 38, losses: 6, winRate: 86.4, change: "-1" },
  { rank: 7, name: "Mica Galvao", country: "BR", rating: 1987, matches: 38, wins: 34, losses: 4, winRate: 89.5, change: "+22" },
  { rank: 8, name: "Kade Ruotolo", country: "US", rating: 1965, matches: 32, wins: 28, losses: 4, winRate: 87.5, change: "+15" },
  { rank: 9, name: "Tye Ruotolo", country: "US", rating: 1952, matches: 30, wins: 26, losses: 4, winRate: 86.7, change: "+9" },
  { rank: 10, name: "Victor Hugo", country: "BR", rating: 1940, matches: 42, wins: 35, losses: 7, winRate: 83.3, change: "-5" },
];

const filters = {
  sport: ["All", "BJJ", "No-Gi", "Wrestling", "Judo", "MMA"],
  gender: ["All", "Male", "Female"],
  period: ["All Time", "This Month", "This Week"],
};

export default function LeaderboardsPage() {
  const [sportFilter, setSportFilter] = useState("All");
  const [genderFilter, setGenderFilter] = useState("All");
  const [periodFilter, setPeriodFilter] = useState("All Time");
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
          Global Leaderboard
        </h1>
        <p className="mt-2 text-slate-600 dark:text-slate-400">
          ELO-based rankings for combat sports athletes worldwide
        </p>
      </div>

      {/* Filters */}
      <div className="mb-6 flex flex-wrap items-center gap-3">
        <input
          type="text"
          placeholder="Search athletes..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="input w-full sm:w-64"
        />

        {Object.entries(filters).map(([key, options]) => (
          <select
            key={key}
            className="input"
            value={key === "sport" ? sportFilter : key === "gender" ? genderFilter : periodFilter}
            onChange={(e) => {
              if (key === "sport") setSportFilter(e.target.value);
              else if (key === "gender") setGenderFilter(e.target.value);
              else setPeriodFilter(e.target.value);
            }}
          >
            {options.map((opt) => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        ))}
      </div>

      {/* Rankings Table */}
      <div className="card overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-surface-850">
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Rank</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Athlete</th>
                <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Rating</th>
                <th className="hidden px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 sm:table-cell">Matches</th>
                <th className="hidden px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 md:table-cell">W/L</th>
                <th className="hidden px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 md:table-cell">Win %</th>
                <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Change</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {demoEntries.map((entry) => (
                <tr
                  key={entry.rank}
                  className="transition-colors hover:bg-slate-50 dark:hover:bg-surface-850"
                >
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold ${
                        entry.rank === 1
                          ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                          : entry.rank === 2
                          ? "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300"
                          : entry.rank === 3
                          ? "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400"
                          : "text-slate-500 dark:text-slate-400"
                      }`}
                    >
                      {entry.rank}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-100 text-sm font-bold text-brand-600 dark:bg-brand-900/30 dark:text-brand-400">
                        {entry.name[0]}
                      </div>
                      <div>
                        <div className="font-medium text-slate-900 dark:text-white">
                          {entry.name}
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">
                          {entry.country}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className="font-mono text-sm font-bold text-slate-900 dark:text-white">
                      {entry.rating}
                    </span>
                  </td>
                  <td className="hidden px-4 py-3 text-right text-sm text-slate-600 dark:text-slate-400 sm:table-cell">
                    {entry.matches}
                  </td>
                  <td className="hidden px-4 py-3 text-right text-sm text-slate-600 dark:text-slate-400 md:table-cell">
                    {entry.wins}-{entry.losses}
                  </td>
                  <td className="hidden px-4 py-3 text-right text-sm text-slate-600 dark:text-slate-400 md:table-cell">
                    {entry.winRate}%
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span
                      className={`text-sm font-medium ${
                        entry.change.startsWith("+")
                          ? "text-emerald-600 dark:text-emerald-400"
                          : "text-red-600 dark:text-red-400"
                      }`}
                    >
                      {entry.change}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between border-t border-slate-200 px-4 py-3 dark:border-slate-700">
          <span className="text-sm text-slate-600 dark:text-slate-400">
            Showing 1-10 of 12,000 athletes
          </span>
          <div className="flex gap-2">
            <button className="btn-secondary px-3 py-1 text-sm" disabled>
              Previous
            </button>
            <button className="btn-secondary px-3 py-1 text-sm">Next</button>
          </div>
        </div>
      </div>
    </div>
  );
}
