export function generateStaticParams() {
  return [{ id: "1" }, { id: "2" }, { id: "3" }];
}

export default function GymDetailPage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <div className="card mb-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-xl bg-brand-100 text-2xl font-bold text-brand-600 dark:bg-brand-900/30 dark:text-brand-400">
            NW
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">New Wave Jiu-Jitsu</h1>
              <svg className="h-5 w-5 text-brand-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <p className="text-slate-600 dark:text-slate-400">Austin, TX, United States</p>
          </div>
          <div className="flex gap-6 text-center">
            <div>
              <div className="text-2xl font-bold text-slate-900 dark:text-white">45</div>
              <div className="text-xs text-slate-500">Members</div>
            </div>
            <div>
              <div className="font-mono text-2xl font-bold text-brand-600 dark:text-brand-400">1680</div>
              <div className="text-xs text-slate-500">Avg Rating</div>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-white">Top Athletes</h2>
        <div className="space-y-3">
          {[
            { rank: 1, name: "Gordon Ryan", rating: 2145, record: "42-6" },
            { rank: 2, name: "Giancarlo Bodoni", rating: 2012, record: "30-5" },
            { rank: 3, name: "Nicky Ryan", rating: 1890, record: "22-4" },
          ].map((a) => (
            <div key={a.rank} className="flex items-center justify-between rounded-lg border border-slate-100 p-3 dark:border-slate-700">
              <div className="flex items-center gap-3">
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-brand-100 text-xs font-bold text-brand-600 dark:bg-brand-900/30 dark:text-brand-400">
                  {a.rank}
                </span>
                <span className="font-medium text-slate-900 dark:text-white">{a.name}</span>
              </div>
              <div className="flex items-center gap-4 text-sm">
                <span className="text-slate-500">{a.record}</span>
                <span className="font-mono font-bold text-brand-600 dark:text-brand-400">{a.rating}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
