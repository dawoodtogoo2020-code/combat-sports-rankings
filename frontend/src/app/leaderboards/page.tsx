"use client";

import { useState, useCallback } from "react";
import { useApi } from "@/hooks/useApi";
import { leaderboards } from "@/lib/api";
import type { LeaderboardResponse, LeaderboardEntry } from "@/types/index";
import { SkeletonRow } from "@/components/ui/Skeleton";
import { EmptyState, RankingsIcon } from "@/components/ui/EmptyState";

type LeaderboardTab = "global" | "country" | "local";

const genderFilters = ["All", "Male", "Female"];
const formatFilters = ["All", "Gi", "No-Gi"];

const countries = [
  { code: "US", name: "United States" },
  { code: "BR", name: "Brazil" },
  { code: "JP", name: "Japan" },
  { code: "GB", name: "United Kingdom" },
  { code: "AU", name: "Australia" },
  { code: "CA", name: "Canada" },
  { code: "MX", name: "Mexico" },
  { code: "AE", name: "UAE" },
  { code: "KR", name: "South Korea" },
  { code: "DE", name: "Germany" },
];

function RankBadge({ rank }: { rank: number }) {
  const cls =
    rank === 1
      ? "bg-gold-100 text-gold-700 dark:bg-gold-900/30 dark:text-gold-400"
      : rank === 2
      ? "bg-surface-200 text-surface-600 dark:bg-surface-700 dark:text-surface-300"
      : rank === 3
      ? "bg-gold-100/60 text-gold-700 dark:bg-gold-900/20 dark:text-gold-500"
      : "text-surface-500 dark:text-surface-400";

  return (
    <span className={`inline-flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold ${cls}`}>
      {rank}
    </span>
  );
}

function ChangeIndicator({ entry }: { entry: LeaderboardEntry }) {
  const change = entry.rating_change_7d;
  if (change == null || change === 0) return <span className="text-xs text-surface-400">—</span>;
  const isUp = change > 0;
  return (
    <span className={`inline-flex items-center gap-0.5 text-sm font-medium ${isUp ? "text-moss-600 dark:text-moss-400" : "text-clay-600 dark:text-clay-400"}`}>
      <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d={isUp ? "M5 15l7-7 7 7" : "M19 9l-7 7-7-7"} />
      </svg>
      {isUp ? "+" : ""}{change}
    </span>
  );
}

/* Mobile card for a single leaderboard entry */
function MobileEntryCard({ entry }: { entry: LeaderboardEntry }) {
  const winRate = entry.win_rate ?? 0;
  return (
    <div className="card flex items-center gap-3 p-4">
      <RankBadge rank={entry.rank} />
      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary-50 text-sm font-bold text-primary-600 dark:bg-primary-950/40 dark:text-primary-400">
        {entry.display_name[0]}
      </div>
      <div className="flex-1 min-w-0">
        <div className="truncate font-medium text-surface-900 dark:text-white">{entry.display_name}</div>
        <div className="text-xs text-surface-500 dark:text-surface-400">
          {entry.country_code || "—"} &middot; {entry.wins}-{entry.losses} ({winRate.toFixed(0)}%)
        </div>
      </div>
      <div className="text-right">
        <div className="font-mono text-sm font-bold text-surface-900 dark:text-white">{entry.elo_rating}</div>
        <ChangeIndicator entry={entry} />
      </div>
    </div>
  );
}

export default function LeaderboardsPage() {
  const [tab, setTab] = useState<LeaderboardTab>("global");
  const [genderFilter, setGenderFilter] = useState("All");
  const [formatFilter, setFormatFilter] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(1);
  const [countryCode, setCountryCode] = useState("US");

  const buildParams = useCallback(() => {
    const params: Record<string, string> = { page: String(page), page_size: "25" };
    if (genderFilter !== "All") params.gender = genderFilter.toLowerCase();
    if (formatFilter === "Gi") params.is_gi = "true";
    if (formatFilter === "No-Gi") params.is_gi = "false";
    return params;
  }, [genderFilter, formatFilter, page]);

  const { data, loading } = useApi<LeaderboardResponse>(
    () => {
      const params = buildParams();
      if (tab === "country") {
        return leaderboards.country(countryCode, params) as Promise<LeaderboardResponse>;
      }
      return leaderboards.global(params) as Promise<LeaderboardResponse>;
    },
    [tab, genderFilter, formatFilter, page, countryCode]
  );

  const entries = data?.entries ?? [];
  const totalCount = data?.total_count ?? 0;
  const totalPages = Math.ceil(totalCount / 25);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-surface-900 dark:text-white">Leaderboard</h1>
        <p className="mt-2 text-surface-500 dark:text-surface-400">
          ELO-based rankings for combat sports athletes
        </p>
      </div>

      {/* Tab Switcher: Global / Country / Local */}
      <div className="mb-6 flex gap-1 rounded-xl bg-surface-100 p-1 dark:bg-surface-800">
        {(["global", "country", "local"] as LeaderboardTab[]).map((t) => (
          <button
            key={t}
            onClick={() => { setTab(t); setPage(1); }}
            className={`flex-1 rounded-lg px-4 py-2 text-sm font-medium capitalize transition-all ${
              tab === t
                ? "bg-white text-surface-900 shadow-soft dark:bg-surface-700 dark:text-white"
                : "text-surface-500 hover:text-surface-900 dark:text-surface-400 dark:hover:text-white"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Country selector (shown only for country tab) */}
      {tab === "country" && (
        <div className="mb-4">
          <select
            value={countryCode}
            onChange={(e) => { setCountryCode(e.target.value); setPage(1); }}
            className="input w-full sm:w-64"
          >
            {countries.map((c) => (
              <option key={c.code} value={c.code}>{c.name}</option>
            ))}
          </select>
        </div>
      )}

      {/* Local tab placeholder */}
      {tab === "local" ? (
        <EmptyState
          icon={<RankingsIcon />}
          title="Local leaderboards coming soon"
          description="Local rankings based on your gym or region will be available in a future update."
        />
      ) : (
        <>
          {/* Filters */}
          <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center">
            <input
              type="text"
              placeholder="Search athletes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input w-full sm:w-72"
            />
            <div className="scrollbar-none flex gap-1.5 overflow-x-auto">
              {genderFilters.map((f) => (
                <button
                  key={f}
                  onClick={() => { setGenderFilter(f); setPage(1); }}
                  className={`flex-shrink-0 rounded-full px-3.5 py-1.5 text-xs font-medium transition-all ${
                    genderFilter === f
                      ? "bg-primary-100 text-primary-700 dark:bg-primary-950/40 dark:text-primary-300"
                      : "bg-surface-100 text-surface-500 hover:bg-surface-200 dark:bg-surface-800 dark:text-surface-400 dark:hover:bg-surface-700"
                  }`}
                >
                  {f}
                </button>
              ))}
              <span className="self-center text-surface-300 dark:text-surface-600">|</span>
              {formatFilters.map((f) => (
                <button
                  key={f}
                  onClick={() => { setFormatFilter(f); setPage(1); }}
                  className={`flex-shrink-0 rounded-full px-3.5 py-1.5 text-xs font-medium transition-all ${
                    formatFilter === f
                      ? "bg-primary-100 text-primary-700 dark:bg-primary-950/40 dark:text-primary-300"
                      : "bg-surface-100 text-surface-500 hover:bg-surface-200 dark:bg-surface-800 dark:text-surface-400 dark:hover:bg-surface-700"
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          {/* Loading */}
          {loading ? (
            <div className="card space-y-1 p-4">
              {Array.from({ length: 10 }).map((_, i) => (
                <SkeletonRow key={i} />
              ))}
            </div>
          ) : entries.length === 0 ? (
            <EmptyState
              icon={<RankingsIcon />}
              title="No rankings yet"
              description="Rankings will appear here once competition data is imported and verified."
            />
          ) : (
            <>
              {/* Mobile cards (below md) */}
              <div className="space-y-2 md:hidden">
                {entries
                  .filter((e) => !searchQuery || e.display_name.toLowerCase().includes(searchQuery.toLowerCase()))
                  .map((entry) => (
                    <MobileEntryCard key={entry.athlete_id} entry={entry} />
                  ))}
              </div>

              {/* Desktop table (md and above) */}
              <div className="card hidden overflow-hidden p-0 md:block">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-surface-200/50 bg-surface-50 dark:border-surface-700/30 dark:bg-surface-850">
                        <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500 dark:text-surface-400">Rank</th>
                        <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500 dark:text-surface-400">Athlete</th>
                        <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-surface-500 dark:text-surface-400">Rating</th>
                        <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-surface-500 dark:text-surface-400">Matches</th>
                        <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-surface-500 dark:text-surface-400">W/L</th>
                        <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-surface-500 dark:text-surface-400">Win %</th>
                        <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-surface-500 dark:text-surface-400">Change</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-surface-100/80 dark:divide-surface-700/30">
                      {entries
                        .filter((e) => !searchQuery || e.display_name.toLowerCase().includes(searchQuery.toLowerCase()))
                        .map((entry) => (
                          <tr key={entry.athlete_id} className="transition-colors hover:bg-surface-50/50 dark:hover:bg-surface-850/50">
                            <td className="px-4 py-3.5"><RankBadge rank={entry.rank} /></td>
                            <td className="px-4 py-3.5">
                              <div className="flex items-center gap-3">
                                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary-50 text-sm font-bold text-primary-600 dark:bg-primary-950/40 dark:text-primary-400">
                                  {entry.display_name[0]}
                                </div>
                                <div>
                                  <div className="font-medium text-surface-900 dark:text-white">{entry.display_name}</div>
                                  <div className="text-xs text-surface-500 dark:text-surface-400">{entry.country_code || "—"}</div>
                                </div>
                              </div>
                            </td>
                            <td className="px-4 py-3.5 text-right font-mono text-sm font-bold text-surface-900 dark:text-white">{entry.elo_rating}</td>
                            <td className="px-4 py-3.5 text-right text-sm text-surface-500 dark:text-surface-400">{entry.total_matches}</td>
                            <td className="px-4 py-3.5 text-right text-sm text-surface-500 dark:text-surface-400">{entry.wins}-{entry.losses}</td>
                            <td className="px-4 py-3.5 text-right text-sm text-surface-500 dark:text-surface-400">{(entry.win_rate ?? 0).toFixed(1)}%</td>
                            <td className="px-4 py-3.5 text-right"><ChangeIndicator entry={entry} /></td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-between border-t border-surface-200/50 px-4 py-3 dark:border-surface-700/30">
                    <span className="text-sm text-surface-500 dark:text-surface-400">
                      Page {page} of {totalPages} ({totalCount} athletes)
                    </span>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => setPage(Math.max(1, page - 1))}
                        disabled={page === 1}
                        className="btn-secondary px-3 py-1.5 text-xs disabled:opacity-40"
                      >
                        Prev
                      </button>
                      <button
                        onClick={() => setPage(Math.min(totalPages, page + 1))}
                        disabled={page >= totalPages}
                        className="btn-secondary px-3 py-1.5 text-xs disabled:opacity-40"
                      >
                        Next
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Mobile pagination */}
              {totalPages > 1 && (
                <div className="mt-4 flex items-center justify-between md:hidden">
                  <button
                    onClick={() => setPage(Math.max(1, page - 1))}
                    disabled={page === 1}
                    className="btn-secondary px-4 py-2 text-sm disabled:opacity-40"
                  >
                    Prev
                  </button>
                  <span className="text-sm text-surface-500">{page} / {totalPages}</span>
                  <button
                    onClick={() => setPage(Math.min(totalPages, page + 1))}
                    disabled={page >= totalPages}
                    className="btn-secondary px-4 py-2 text-sm disabled:opacity-40"
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}
