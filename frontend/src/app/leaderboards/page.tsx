"use client";

import { useState } from "react";

const demoEntries = [
  { rank: 1, name: "Gordon Ryan", country: "US", rating: 2145, matches: 48, wins: 42, losses: 6, winRate: 87.5, change: "+12", weightClass: "Ultra Heavy", belt: "Black", format: "No-Gi" },
  { rank: 2, name: "Andre Galvao", country: "BR", rating: 2098, matches: 62, wins: 54, losses: 8, winRate: 87.1, change: "+5", weightClass: "Medium Heavy", belt: "Black", format: "Both" },
  { rank: 3, name: "Felipe Pena", country: "BR", rating: 2067, matches: 55, wins: 47, losses: 8, winRate: 85.5, change: "-3", weightClass: "Heavy", belt: "Black", format: "Both" },
  { rank: 4, name: "Nicholas Meregali", country: "BR", rating: 2034, matches: 41, wins: 36, losses: 5, winRate: 87.8, change: "+18", weightClass: "Super Heavy", belt: "Black", format: "No-Gi" },
  { rank: 5, name: "Giancarlo Bodoni", country: "US", rating: 2012, matches: 35, wins: 30, losses: 5, winRate: 85.7, change: "+8", weightClass: "Medium Heavy", belt: "Black", format: "No-Gi" },
  { rank: 6, name: "Kaynan Duarte", country: "BR", rating: 1998, matches: 44, wins: 38, losses: 6, winRate: 86.4, change: "-1", weightClass: "Ultra Heavy", belt: "Black", format: "Both" },
  { rank: 7, name: "Mica Galvao", country: "BR", rating: 1987, matches: 38, wins: 34, losses: 4, winRate: 89.5, change: "+22", weightClass: "Middle", belt: "Black", format: "Both" },
  { rank: 8, name: "Kade Ruotolo", country: "US", rating: 1965, matches: 32, wins: 28, losses: 4, winRate: 87.5, change: "+15", weightClass: "Light", belt: "Black", format: "No-Gi" },
  { rank: 9, name: "Tye Ruotolo", country: "US", rating: 1952, matches: 30, wins: 26, losses: 4, winRate: 86.7, change: "+9", weightClass: "Middle", belt: "Brown", format: "No-Gi" },
  { rank: 10, name: "Victor Hugo", country: "BR", rating: 1940, matches: 42, wins: 35, losses: 7, winRate: 83.3, change: "-5", weightClass: "Super Heavy", belt: "Black", format: "Both" },
];

const sportFilters = ["All", "BJJ", "No-Gi", "Wrestling", "Judo", "MMA"];
const genderFilters = ["All", "Male", "Female"];
const periodFilters = ["All Time", "This Month", "This Week"];
const weightFilters = ["All", "Rooster", "Light Feather", "Feather", "Light", "Middle", "Medium Heavy", "Heavy", "Super Heavy", "Ultra Heavy"];
const beltFilters = ["All", "Black", "Brown", "Purple", "Blue", "White"];
const formatFilters = ["All", "Gi", "No-Gi"];

type FilterGroupProps = {
  label: string;
  options: string[];
  active: string;
  onChange: (v: string) => void;
};

function FilterGroup({ label, options, active, onChange }: FilterGroupProps) {
  return (
    <div className="flex items-center gap-1.5">
      <span className="mr-1 flex-shrink-0 text-xs font-medium text-surface-400 dark:text-surface-500">{label}</span>
      <div className="scrollbar-none flex gap-1.5 overflow-x-auto">
        {options.map((f) => (
          <button
            key={f}
            onClick={() => onChange(f)}
            className={`flex-shrink-0 rounded-full px-3 py-1.5 text-xs font-medium transition-all ${
              active === f
                ? "bg-primary-100 text-primary-700 dark:bg-primary-950/40 dark:text-primary-300"
                : "bg-surface-100 text-surface-500 hover:bg-surface-200 dark:bg-surface-800 dark:text-surface-400 dark:hover:bg-surface-700"
            }`}
          >
            {f}
          </button>
        ))}
      </div>
    </div>
  );
}

export default function LeaderboardsPage() {
  const [sportFilter, setSportFilter] = useState("All");
  const [genderFilter, setGenderFilter] = useState("All");
  const [periodFilter, setPeriodFilter] = useState("All Time");
  const [weightFilter, setWeightFilter] = useState("All");
  const [beltFilter, setBeltFilter] = useState("All");
  const [formatFilter, setFormatFilter] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-surface-900 dark:text-white">
          Global Leaderboard
        </h1>
        <p className="mt-2 text-surface-500 dark:text-surface-400">
          ELO-based rankings for combat sports athletes worldwide
        </p>
      </div>

      {/* Filters */}
      <div className="mb-6 space-y-3">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <input
            type="text"
            placeholder="Search athletes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input w-full sm:w-72"
          />
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className={`flex items-center gap-1.5 rounded-full px-3.5 py-1.5 text-xs font-medium transition-all ${
              showAdvanced
                ? "bg-primary-100 text-primary-700 dark:bg-primary-950/40 dark:text-primary-300"
                : "bg-surface-100 text-surface-500 hover:bg-surface-200 dark:bg-surface-800 dark:text-surface-400 dark:hover:bg-surface-700"
            }`}
          >
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            Filters
          </button>
        </div>

        {/* Basic filter row — horizontally scrollable on mobile */}
        <div className="scrollbar-none -mx-4 flex items-center gap-2 overflow-x-auto px-4 sm:mx-0 sm:flex-wrap sm:overflow-visible sm:px-0">
          {sportFilters.map((f) => (
            <button
              key={f}
              onClick={() => setSportFilter(f)}
              className={`rounded-full px-3.5 py-1.5 text-xs font-medium transition-all ${
                sportFilter === f
                  ? "bg-primary-100 text-primary-700 dark:bg-primary-950/40 dark:text-primary-300"
                  : "bg-surface-100 text-surface-500 hover:bg-surface-200 dark:bg-surface-800 dark:text-surface-400 dark:hover:bg-surface-700"
              }`}
            >
              {f}
            </button>
          ))}
          <span className="mx-1 self-center text-surface-300 dark:text-surface-600">|</span>
          {genderFilters.map((f) => (
            <button
              key={f}
              onClick={() => setGenderFilter(f)}
              className={`rounded-full px-3.5 py-1.5 text-xs font-medium transition-all ${
                genderFilter === f
                  ? "bg-primary-100 text-primary-700 dark:bg-primary-950/40 dark:text-primary-300"
                  : "bg-surface-100 text-surface-500 hover:bg-surface-200 dark:bg-surface-800 dark:text-surface-400 dark:hover:bg-surface-700"
              }`}
            >
              {f}
            </button>
          ))}
          <span className="mx-1 self-center text-surface-300 dark:text-surface-600">|</span>
          {periodFilters.map((f) => (
            <button
              key={f}
              onClick={() => setPeriodFilter(f)}
              className={`rounded-full px-3.5 py-1.5 text-xs font-medium transition-all ${
                periodFilter === f
                  ? "bg-primary-100 text-primary-700 dark:bg-primary-950/40 dark:text-primary-300"
                  : "bg-surface-100 text-surface-500 hover:bg-surface-200 dark:bg-surface-800 dark:text-surface-400 dark:hover:bg-surface-700"
              }`}
            >
              {f}
            </button>
          ))}
        </div>

        {/* Advanced filters */}
        {showAdvanced && (
          <div className="card space-y-3 bg-surface-50 dark:bg-surface-850">
            <FilterGroup label="Weight" options={weightFilters} active={weightFilter} onChange={setWeightFilter} />
            <FilterGroup label="Belt" options={beltFilters} active={beltFilter} onChange={setBeltFilter} />
            <FilterGroup label="Format" options={formatFilters} active={formatFilter} onChange={setFormatFilter} />
          </div>
        )}
      </div>

      {/* Rankings Table */}
      <div className="card overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-surface-200/50 bg-surface-50 dark:border-surface-700/30 dark:bg-surface-850">
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500 dark:text-surface-400">Rank</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500 dark:text-surface-400">Athlete</th>
                <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-surface-500 dark:text-surface-400">Rating</th>
                <th className="hidden px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-surface-500 dark:text-surface-400 sm:table-cell">Matches</th>
                <th className="hidden px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-surface-500 dark:text-surface-400 md:table-cell">W/L</th>
                <th className="hidden px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-surface-500 dark:text-surface-400 md:table-cell">Win %</th>
                <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-surface-500 dark:text-surface-400">Change</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-100/80 dark:divide-surface-700/30">
              {demoEntries.map((entry) => (
                <tr
                  key={entry.rank}
                  className="transition-colors hover:bg-surface-50/50 dark:hover:bg-surface-850/50"
                >
                  <td className="px-4 py-3.5">
                    <span
                      className={`inline-flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold ${
                        entry.rank === 1
                          ? "bg-gold-100 text-gold-700 dark:bg-gold-900/30 dark:text-gold-400"
                          : entry.rank === 2
                          ? "bg-surface-200 text-surface-600 dark:bg-surface-700 dark:text-surface-300"
                          : entry.rank === 3
                          ? "bg-gold-100/60 text-gold-700 dark:bg-gold-900/20 dark:text-gold-500"
                          : "text-surface-500 dark:text-surface-400"
                      }`}
                    >
                      {entry.rank}
                    </span>
                  </td>
                  <td className="px-4 py-3.5">
                    <div className="flex items-center gap-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary-50 text-sm font-bold text-primary-600 dark:bg-primary-950/40 dark:text-primary-400">
                        {entry.name[0]}
                      </div>
                      <div>
                        <div className="font-medium text-surface-900 dark:text-white">
                          {entry.name}
                        </div>
                        <div className="text-xs text-surface-500 dark:text-surface-400">
                          {entry.country} &middot; {entry.weightClass}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3.5 text-right">
                    <span className="font-mono text-sm font-bold text-surface-900 dark:text-white">
                      {entry.rating}
                    </span>
                  </td>
                  <td className="hidden px-4 py-3.5 text-right text-sm text-surface-500 dark:text-surface-400 sm:table-cell">
                    {entry.matches}
                  </td>
                  <td className="hidden px-4 py-3.5 text-right text-sm text-surface-500 dark:text-surface-400 md:table-cell">
                    {entry.wins}-{entry.losses}
                  </td>
                  <td className="hidden px-4 py-3.5 text-right text-sm text-surface-500 dark:text-surface-400 md:table-cell">
                    {entry.winRate}%
                  </td>
                  <td className="px-4 py-3.5 text-right">
                    <span
                      className={`inline-flex items-center gap-0.5 text-sm font-medium ${
                        entry.change.startsWith("+")
                          ? "text-moss-600 dark:text-moss-400"
                          : "text-clay-600 dark:text-clay-400"
                      }`}
                    >
                      {entry.change.startsWith("+") ? (
                        <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 15l7-7 7 7" /></svg>
                      ) : (
                        <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 9l-7 7-7-7" /></svg>
                      )}
                      {entry.change}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between border-t border-surface-200/50 px-4 py-3 dark:border-surface-700/30">
          <span className="hidden text-sm text-surface-500 dark:text-surface-400 sm:inline">
            Showing 1-10 of 12,000 athletes
          </span>
          <span className="text-xs text-surface-500 dark:text-surface-400 sm:hidden">
            1-10 of 12,000
          </span>
          <div className="flex items-center gap-1">
            <button className="btn-secondary px-3 py-1.5 text-xs" disabled>
              Prev
            </button>
            <button className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-100 text-xs font-bold text-primary-700 dark:bg-primary-950/40 dark:text-primary-300">1</button>
            <button className="hidden h-8 w-8 items-center justify-center rounded-lg text-xs text-surface-500 hover:bg-surface-100 dark:text-surface-400 dark:hover:bg-surface-800 sm:flex">2</button>
            <button className="hidden h-8 w-8 items-center justify-center rounded-lg text-xs text-surface-500 hover:bg-surface-100 dark:text-surface-400 dark:hover:bg-surface-800 sm:flex">3</button>
            <span className="hidden px-1 text-surface-400 sm:inline">...</span>
            <button className="hidden h-8 w-8 items-center justify-center rounded-lg text-xs text-surface-500 hover:bg-surface-100 dark:text-surface-400 dark:hover:bg-surface-800 sm:flex">120</button>
            <button className="btn-secondary px-3 py-1.5 text-xs">Next</button>
          </div>
        </div>
      </div>
    </div>
  );
}
