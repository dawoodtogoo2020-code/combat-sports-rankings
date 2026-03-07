const athlete = {
  id: "1",
  display_name: "Gordon Ryan",
  first_name: "Gordon",
  last_name: "Ryan",
  country: "United States",
  country_code: "US",
  gender: "male",
  belt: "Black",
  years_training: 12,
  gym: "New Wave Jiu-Jitsu",
  bio: "Multiple-time ADCC champion. Considered one of the greatest grapplers of all time.",
  elo_rating: 2145,
  gi_rating: 2020,
  nogi_rating: 2270,
  peak_rating: 2180,
  total_matches: 48,
  wins: 42,
  losses: 6,
  draws: 0,
  submissions: 28,
  competitor_points: 4200,
};

const ratingHistory = [
  { date: "2024-01", rating: 1950 },
  { date: "2024-03", rating: 2010 },
  { date: "2024-05", rating: 2050 },
  { date: "2024-07", rating: 2090 },
  { date: "2024-09", rating: 2120 },
  { date: "2024-11", rating: 2145 },
];

const recentMatches = [
  { opponent: "Felipe Pena", result: "W", method: "Submission (RNC)", event: "ADCC 2024", eloChange: "+18" },
  { opponent: "Andre Galvao", result: "W", method: "Points (8-2)", event: "WNO Championships", eloChange: "+12" },
  { opponent: "Nicholas Meregali", result: "W", method: "Submission (Heel Hook)", event: "CJI 2024", eloChange: "+15" },
  { opponent: "Kaynan Duarte", result: "L", method: "Points (2-4)", event: "ADCC Trials", eloChange: "-8" },
  { opponent: "Victor Hugo", result: "W", method: "Decision", event: "WNO", eloChange: "+6" },
];

export function generateStaticParams() {
  return [{ id: "1" }, { id: "2" }, { id: "3" }];
}

function RatingChart() {
  const min = Math.min(...ratingHistory.map((p) => p.rating));
  const max = Math.max(...ratingHistory.map((p) => p.rating));
  const range = max - min || 1;
  const padding = 10;
  const width = 400;
  const height = 160;
  const usableH = height - padding * 2;
  const usableW = width - padding * 2;

  const points = ratingHistory.map((p, i) => {
    const x = padding + (i / (ratingHistory.length - 1)) * usableW;
    const y = padding + usableH - ((p.rating - min) / range) * usableH;
    return { x, y, ...p };
  });

  const linePath = points.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");
  const areaPath = `${linePath} L ${points[points.length - 1].x} ${height} L ${points[0].x} ${height} Z`;

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
      {points.map((p, i) => (
        <circle key={i} cx={p.x} cy={p.y} r="3.5" fill="rgb(160, 111, 204)" stroke="white" strokeWidth="2" />
      ))}
    </svg>
  );
}

export default function AthleteDetailPage() {
  const winRate = Math.round((athlete.wins / athlete.total_matches) * 100);
  const subRate = Math.round((athlete.submissions / athlete.wins) * 100);

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
              <svg className="h-5 w-5 text-primary-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <p className="mt-1 text-surface-500 dark:text-surface-400">
              {athlete.country} &middot; {athlete.belt} Belt &middot; {athlete.years_training} years training
            </p>
            <p className="mt-1 text-sm text-surface-400 dark:text-surface-500">
              {athlete.gym}
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
        </div>

        {/* Rating Graph */}
        <div className="card lg:col-span-2">
          <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-white">Rating Progression</h2>
          <div className="mb-2">
            <RatingChart />
          </div>
          <div className="flex justify-between px-1 text-xs text-surface-400">
            {ratingHistory.map((p) => (
              <span key={p.date}>{p.date}</span>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Matches */}
      <div className="card mt-6">
        <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-white">Recent Matches</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-surface-200/50 dark:border-surface-700/30">
                <th className="pb-2.5 text-left text-xs font-semibold uppercase text-surface-500">Result</th>
                <th className="pb-2.5 text-left text-xs font-semibold uppercase text-surface-500">Opponent</th>
                <th className="pb-2.5 text-left text-xs font-semibold uppercase text-surface-500">Method</th>
                <th className="pb-2.5 text-left text-xs font-semibold uppercase text-surface-500">Event</th>
                <th className="pb-2.5 text-right text-xs font-semibold uppercase text-surface-500">ELO</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-100/80 dark:divide-surface-700/30">
              {recentMatches.map((m, i) => (
                <tr key={i}>
                  <td className="py-3">
                    <span
                      className={`badge ${
                        m.result === "W"
                          ? "bg-moss-100 text-moss-700 dark:bg-moss-900/30 dark:text-moss-400"
                          : "bg-clay-100 text-clay-700 dark:bg-clay-900/30 dark:text-clay-400"
                      }`}
                    >
                      {m.result === "W" ? "WIN" : "LOSS"}
                    </span>
                  </td>
                  <td className="py-3 text-sm font-medium text-surface-900 dark:text-white">
                    {m.opponent}
                  </td>
                  <td className="py-3 text-sm text-surface-500 dark:text-surface-400">{m.method}</td>
                  <td className="py-3 text-sm text-surface-500 dark:text-surface-400">{m.event}</td>
                  <td className="py-3 text-right">
                    <span
                      className={`font-mono text-sm font-medium ${
                        m.eloChange.startsWith("+") ? "rating-up" : "rating-down"
                      }`}
                    >
                      {m.eloChange}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
