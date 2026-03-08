"use client";

import { useParams } from "next/navigation";
import { useApi } from "@/hooks/useApi";
import { athletes as athletesApi } from "@/lib/api";
import type { Athlete, RatingPoint } from "@/types/index";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState, AthletesIcon } from "@/components/ui/EmptyState";

function RatingChart({ points }: { points: RatingPoint[] }) {
  if (points.length < 2) return null;

  const ratings = points.map((p) => p.rating_after);
  const min = Math.min(...ratings);
  const max = Math.max(...ratings);
  const range = max - min || 1;
  const padding = 10;
  const width = 400;
  const height = 160;
  const usableH = height - padding * 2;
  const usableW = width - padding * 2;

  const chartPoints = points.map((p, i) => {
    const x = padding + (i / (points.length - 1)) * usableW;
    const y = padding + usableH - ((p.rating_after - min) / range) * usableH;
    return { x, y, ...p };
  });

  const linePath = chartPoints.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");
  const areaPath = `${linePath} L ${chartPoints[chartPoints.length - 1].x} ${height} L ${chartPoints[0].x} ${height} Z`;

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full" preserveAspectRatio="none">
      <defs>
        <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="rgb(160, 111, 204)" stopOpacity="0.3" />
          <stop offset="100%" stopColor="rgb(160, 111, 204)" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={areaPath} fill="url(#chartGrad)" />
      <path d={linePath} fill="none" stroke="rgb(160, 111, 204)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      {chartPoints.map((p, i) => (
        <circle key={i} cx={p.x} cy={p.y} r="3.5" fill="rgb(160, 111, 204)" stroke="white" strokeWidth="2" />
      ))}
    </svg>
  );
}

export default function AthleteDetailClient() {
  const params = useParams();
  const id = params?.id as string;

  const { data: athlete, loading } = useApi<Athlete>(
    () => athletesApi.get(id) as Promise<Athlete>,
    [id]
  );
  const { data: ratingHistory } = useApi<RatingPoint[]>(
    () => athletesApi.ratingHistory(id) as Promise<RatingPoint[]>,
    [id]
  );

  if (loading) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        <div className="card mb-6">
          <div className="flex flex-col gap-6 sm:flex-row">
            <Skeleton className="h-24 w-24 rounded-2xl" />
            <div className="flex-1 space-y-3">
              <Skeleton className="h-7 w-48" />
              <Skeleton className="h-4 w-64" />
              <Skeleton className="h-4 w-40" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!athlete) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        <EmptyState
          icon={<AthletesIcon />}
          title="Athlete not found"
          description="This athlete profile doesn't exist or hasn't been imported yet."
          actionLabel="Browse Athletes"
          actionHref="/athletes"
        />
      </div>
    );
  }

  const winRate = athlete.total_matches > 0 ? Math.round((athlete.wins / athlete.total_matches) * 100) : 0;
  const subRate = athlete.wins > 0 ? Math.round((athlete.submissions / athlete.wins) * 100) : 0;

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      {/* Profile Header */}
      <div className="card mb-6">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-start">
          <div className="flex h-24 w-24 items-center justify-center rounded-2xl bg-primary-50 text-3xl font-bold text-primary-600 dark:bg-primary-950/40 dark:text-primary-400">
            {athlete.first_name[0]}{athlete.last_name[0]}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-surface-900 dark:text-white">
                {athlete.display_name}
              </h1>
              {athlete.is_verified && (
                <svg className="h-5 w-5 text-primary-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              )}
            </div>
            <p className="mt-1 text-surface-500 dark:text-surface-400">
              {athlete.country || "Unknown"} {athlete.years_training ? `\u00b7 ${athlete.years_training} years training` : ""}
            </p>
            {athlete.bio && (
              <p className="mt-3 text-sm text-surface-600 dark:text-surface-400">{athlete.bio}</p>
            )}
          </div>
          <div className="text-center sm:text-right">
            <div className="font-mono text-4xl font-bold text-primary-600 dark:text-primary-400">
              {athlete.elo_rating}
            </div>
            <div className="text-sm text-surface-500 dark:text-surface-400">Overall ELO</div>
            <div className="mt-2 text-xs text-surface-400 dark:text-surface-500">
              Peak: {athlete.peak_rating}
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Stats */}
        <div className="card lg:col-span-1">
          <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-white">Statistics</h2>
          <div className="space-y-3">
            {[
              { label: "Total Matches", value: athlete.total_matches },
              { label: "Wins", value: athlete.wins, className: "text-moss-600 dark:text-moss-400" },
              { label: "Losses", value: athlete.losses, className: "text-clay-600 dark:text-clay-400" },
              { label: "Draws", value: athlete.draws },
              { label: "Submissions", value: athlete.submissions },
              { label: "Win Rate", value: `${winRate}%` },
              { label: "Sub Rate", value: `${subRate}%` },
              { label: "Gi Rating", value: athlete.gi_rating },
              { label: "No-Gi Rating", value: athlete.nogi_rating },
              { label: "Competitor Points", value: athlete.competitor_points },
            ].map((stat) => (
              <div key={stat.label} className="flex items-center justify-between">
                <span className="text-sm text-surface-500 dark:text-surface-400">{stat.label}</span>
                <span className={`font-mono text-sm font-semibold ${stat.className || "text-surface-900 dark:text-white"}`}>
                  {stat.value}
                </span>
              </div>
            ))}
          </div>

          {/* Win/Loss bar */}
          {athlete.total_matches > 0 && (
            <div className="mt-6">
              <div className="mb-1.5 flex justify-between text-xs text-surface-500">
                <span>{athlete.wins}W</span>
                <span>{athlete.losses}L</span>
              </div>
              <div className="flex h-2 overflow-hidden rounded-full bg-surface-100 dark:bg-surface-700">
                <div className="rounded-full bg-moss-500" style={{ width: `${winRate}%` }} />
                <div className="rounded-full bg-clay-400" style={{ width: `${100 - winRate}%` }} />
              </div>
            </div>
          )}
        </div>

        {/* Rating Graph */}
        <div className="card lg:col-span-2">
          <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-white">Rating Progression</h2>
          {ratingHistory && ratingHistory.length >= 2 ? (
            <div className="mb-2">
              <RatingChart points={ratingHistory} />
            </div>
          ) : (
            <div className="flex h-40 items-center justify-center text-sm text-surface-400">
              Rating history will appear after multiple competitions
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
