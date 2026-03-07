import Link from "next/link";

const stats = [
  { label: "Athletes Ranked", value: "12,000+" },
  { label: "Matches Tracked", value: "85,000+" },
  { label: "Events Indexed", value: "2,400+" },
  { label: "Countries", value: "90+" },
];

const features = [
  {
    title: "ELO Rankings",
    description: "Modified chess-style ELO system adapted for combat sports with competition tier weighting.",
    icon: "chart",
  },
  {
    title: "Multi-Sport",
    description: "BJJ Gi & No-Gi, Wrestling, Judo, MMA, and more — all in one platform.",
    icon: "globe",
  },
  {
    title: "Live Results",
    description: "Competition data imported from AJP, ADCC, NAGA, Grappling Industries, and more.",
    icon: "zap",
  },
  {
    title: "Gym Leaderboards",
    description: "Gyms can track their members' rankings and run internal competitions.",
    icon: "users",
  },
];

export default function HomePage() {
  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-b from-surface-900 to-surface-950 py-24 text-white dark:from-surface-950 dark:to-black">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-brand-900/20 via-transparent to-transparent" />
        <div className="relative mx-auto max-w-7xl px-4 text-center sm:px-6">
          <div className="mx-auto max-w-3xl">
            <h1 className="text-4xl font-extrabold tracking-tight sm:text-6xl">
              The Global
              <span className="block bg-gradient-to-r from-brand-400 to-blue-300 bg-clip-text text-transparent">
                Combat Sports Rankings
              </span>
            </h1>
            <p className="mt-6 text-lg text-slate-300 sm:text-xl">
              ELO-based ranking system for BJJ, grappling, and combat sports athletes worldwide.
              Track your progress, compare with the best, and climb the leaderboard.
            </p>
            <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
              <Link href="/leaderboards" className="btn-primary px-8 py-3 text-base">
                View Rankings
              </Link>
              <Link
                href="/auth"
                className="btn rounded-lg border border-slate-600 px-8 py-3 text-base text-white hover:bg-white/10"
              >
                Create Account
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="border-b border-slate-200 bg-white py-12 dark:border-slate-800 dark:bg-surface-900">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-3xl font-bold text-brand-600 dark:text-brand-400">
                  {stat.value}
                </div>
                <div className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white">
              How It Works
            </h2>
            <p className="mt-4 text-lg text-slate-600 dark:text-slate-400">
              A data-driven approach to ranking combat sports athletes globally.
            </p>
          </div>

          <div className="mt-16 grid gap-8 md:grid-cols-2 lg:grid-cols-4">
            {features.map((feature) => (
              <div key={feature.title} className="card text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-brand-100 dark:bg-brand-900/30">
                  <svg className="h-6 w-6 text-brand-600 dark:text-brand-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
                <h3 className="mt-4 text-lg font-semibold text-slate-900 dark:text-white">
                  {feature.title}
                </h3>
                <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-brand-600 py-16 dark:bg-brand-700">
        <div className="mx-auto max-w-7xl px-4 text-center sm:px-6">
          <h2 className="text-3xl font-bold text-white">
            Ready to track your ranking?
          </h2>
          <p className="mt-4 text-lg text-brand-100">
            Join the global combat sports community and see where you stand.
          </p>
          <Link
            href="/auth"
            className="mt-8 inline-flex items-center rounded-lg bg-white px-8 py-3 text-base font-medium text-brand-600 hover:bg-brand-50"
          >
            Get Started Free
          </Link>
        </div>
      </section>
    </div>
  );
}
