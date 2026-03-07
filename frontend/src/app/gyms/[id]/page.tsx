import Link from "next/link";

export function generateStaticParams() {
  return [{ id: "1" }, { id: "2" }, { id: "3" }];
}

const gymData = {
  name: "New Wave Jiu-Jitsu",
  city: "Austin, TX",
  country: "United States",
  members: 45,
  avgRating: 1680,
  founded: "2017",
  headCoach: "John Danaher",
  style: "No-Gi",
  description: "Elite grappling academy focused on systematic approaches to submission grappling and no-gi jiu-jitsu.",
};

const topAthletes = [
  { rank: 1, name: "Gordon Ryan", rating: 2145, record: "42-6", change: "+12" },
  { rank: 2, name: "Giancarlo Bodoni", rating: 2012, record: "30-5", change: "+8" },
  { rank: 3, name: "Nicky Ryan", rating: 1890, record: "22-4", change: "+15" },
];

export default function GymDetailPage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      {/* Breadcrumb */}
      <div className="mb-6">
        <Link href="/gyms" className="text-sm text-surface-500 hover:text-primary-600 dark:text-surface-400 dark:hover:text-primary-400 transition-colors">
          &larr; Back to Gyms
        </Link>
      </div>

      {/* Header Card */}
      <div className="card mb-6">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-start">
          <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-primary-50 text-3xl font-bold text-primary-600 dark:bg-primary-950/40 dark:text-primary-400">
            NW
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-surface-900 dark:text-white">{gymData.name}</h1>
              <svg className="h-5 w-5 text-primary-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <p className="mt-1 text-surface-500 dark:text-surface-400">
              {gymData.city}, {gymData.country}
            </p>
            <p className="mt-3 text-sm text-surface-600 dark:text-surface-300">
              {gymData.description}
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              <span className="badge bg-primary-50 text-primary-700 dark:bg-primary-950/30 dark:text-primary-300">
                {gymData.style}
              </span>
              <span className="badge bg-surface-100 text-surface-600 dark:bg-surface-800 dark:text-surface-300">
                Est. {gymData.founded}
              </span>
              <span className="badge bg-surface-100 text-surface-600 dark:bg-surface-800 dark:text-surface-300">
                Coach: {gymData.headCoach}
              </span>
            </div>
          </div>
          <div className="flex gap-8 text-center sm:flex-col sm:gap-4">
            <div>
              <div className="text-2xl font-bold text-surface-900 dark:text-white">{gymData.members}</div>
              <div className="text-xs text-surface-500 dark:text-surface-400">Members</div>
            </div>
            <div>
              <div className="font-mono text-2xl font-bold text-primary-600 dark:text-primary-400">{gymData.avgRating}</div>
              <div className="text-xs text-surface-500 dark:text-surface-400">Avg Rating</div>
            </div>
          </div>
        </div>
      </div>

      {/* Top Athletes */}
      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-white">Top Athletes</h2>
        <div className="space-y-3">
          {topAthletes.map((a) => (
            <div
              key={a.rank}
              className="flex items-center justify-between rounded-xl border border-surface-100 p-4 transition-colors hover:bg-surface-50 dark:border-surface-700/30 dark:hover:bg-surface-850/50"
            >
              <div className="flex items-center gap-3">
                <span
                  className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold ${
                    a.rank === 1
                      ? "bg-gold-100 text-gold-700 dark:bg-gold-900/30 dark:text-gold-400"
                      : a.rank === 2
                      ? "bg-surface-200 text-surface-600 dark:bg-surface-700 dark:text-surface-300"
                      : "bg-gold-100/60 text-gold-700 dark:bg-gold-900/20 dark:text-gold-500"
                  }`}
                >
                  {a.rank}
                </span>
                <span className="font-medium text-surface-900 dark:text-white">{a.name}</span>
              </div>
              <div className="flex items-center gap-5 text-sm">
                <span className="text-surface-500 dark:text-surface-400">{a.record}</span>
                <span className="font-mono font-bold text-primary-600 dark:text-primary-400">{a.rating}</span>
                <span className={`inline-flex items-center gap-0.5 text-xs font-medium ${
                  a.change.startsWith("+")
                    ? "text-moss-600 dark:text-moss-400"
                    : "text-clay-600 dark:text-clay-400"
                }`}>
                  {a.change.startsWith("+") ? (
                    <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 15l7-7 7 7" /></svg>
                  ) : (
                    <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 9l-7 7-7-7" /></svg>
                  )}
                  {a.change}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
