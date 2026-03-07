"use client";

export default function EventDetailPage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <div className="card mb-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
                ADCC World Championships 2025
              </h1>
              <span className="badge badge-gold">ELITE</span>
            </div>
            <p className="mt-2 text-slate-600 dark:text-slate-400">
              September 20-21, 2025 &middot; Las Vegas, USA &middot; ADCC
            </p>
          </div>
          <div className="flex gap-2">
            <span className="badge bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300">No-Gi</span>
            <span className="badge bg-brand-100 text-brand-700 dark:bg-brand-900/30 dark:text-brand-400">1.6x K-Factor</span>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="card lg:col-span-1">
          <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-white">Event Info</h2>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Matches</span>
              <span className="font-medium text-slate-900 dark:text-white">248</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Competitors</span>
              <span className="font-medium text-slate-900 dark:text-white">128</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Divisions</span>
              <span className="font-medium text-slate-900 dark:text-white">16</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">CP Multiplier</span>
              <span className="font-medium text-slate-900 dark:text-white">2.0x</span>
            </div>
          </div>
        </div>

        <div className="card lg:col-span-2">
          <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-white">Match Results</h2>
          <div className="space-y-3">
            {[
              { winner: "Gordon Ryan", loser: "Felipe Pena", method: "Submission (RNC)", division: "-99kg", round: "Final" },
              { winner: "Mica Galvao", loser: "Kade Ruotolo", method: "Points (4-2)", division: "-77kg", round: "Final" },
              { winner: "Nicholas Meregali", loser: "Kaynan Duarte", method: "Submission (Collar Choke)", division: "+99kg", round: "Semi-Final" },
            ].map((m, i) => (
              <div key={i} className="flex items-center justify-between rounded-lg border border-slate-100 p-3 dark:border-slate-700">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">{m.winner}</span>
                    <span className="text-xs text-slate-400">def.</span>
                    <span className="text-sm text-slate-600 dark:text-slate-400">{m.loser}</span>
                  </div>
                  <div className="mt-1 text-xs text-slate-500">{m.method}</div>
                </div>
                <div className="text-right text-xs text-slate-500">
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
