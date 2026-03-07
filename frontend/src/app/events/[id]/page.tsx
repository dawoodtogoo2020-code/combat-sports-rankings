export function generateStaticParams() {
  return [{ id: "1" }, { id: "2" }, { id: "3" }];
}

export default function EventDetailPage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      {/* Event Header */}
      <div className="card mb-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-surface-900 dark:text-white">
                ADCC World Championships 2025
              </h1>
              <span className="badge badge-gold">ELITE</span>
            </div>
            <p className="mt-2 text-surface-500 dark:text-surface-400">
              September 20-21, 2025 &middot; Las Vegas, USA &middot; ADCC
            </p>
          </div>
          <div className="flex gap-2">
            <span className="badge bg-surface-100 text-surface-600 dark:bg-surface-700 dark:text-surface-300">No-Gi</span>
            <span className="badge bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400">1.6x K-Factor</span>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="card lg:col-span-1">
          <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-white">Event Info</h2>
          <div className="space-y-3 text-sm">
            {[
              { label: "Matches", value: "248" },
              { label: "Competitors", value: "128" },
              { label: "Divisions", value: "16" },
              { label: "CP Multiplier", value: "2.0x" },
            ].map((item) => (
              <div key={item.label} className="flex justify-between">
                <span className="text-surface-500 dark:text-surface-400">{item.label}</span>
                <span className="font-medium text-surface-900 dark:text-white">{item.value}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card lg:col-span-2">
          <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-white">Match Results</h2>
          <div className="space-y-3">
            {[
              { winner: "Gordon Ryan", loser: "Felipe Pena", method: "Submission (RNC)", division: "-99kg", round: "Final" },
              { winner: "Mica Galvao", loser: "Kade Ruotolo", method: "Points (4-2)", division: "-77kg", round: "Final" },
              { winner: "Nicholas Meregali", loser: "Kaynan Duarte", method: "Submission (Collar Choke)", division: "+99kg", round: "Semi-Final" },
            ].map((m, i) => (
              <div key={i} className="flex items-center justify-between rounded-xl border border-surface-100 p-3.5 dark:border-surface-700/50">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-moss-600 dark:text-moss-400">{m.winner}</span>
                    <span className="text-xs text-surface-400">def.</span>
                    <span className="text-sm text-surface-500 dark:text-surface-400">{m.loser}</span>
                  </div>
                  <div className="mt-1 text-xs text-surface-400">{m.method}</div>
                </div>
                <div className="text-right text-xs text-surface-400">
                  <div>{m.division}</div>
                  <div>{m.round}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
