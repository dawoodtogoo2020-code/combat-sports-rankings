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
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
      </svg>
    ),
  },
  {
    title: "Multi-Sport",
    description: "BJJ Gi & No-Gi, Wrestling, Judo, MMA, and more — all in one platform.",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
      </svg>
    ),
  },
  {
    title: "Live Results",
    description: "Competition data imported from AJP, ADCC, NAGA, Grappling Industries, and more.",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
  },
  {
    title: "Gym Leaderboards",
    description: "Gyms can track their members' rankings and run internal competitions.",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    ),
  },
];

export default function HomePage() {
  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden bg-surface-900 py-28 text-white dark:bg-surface-950">
        {/* Atmospheric background layers */}
        <div className="absolute inset-0 bg-gradient-to-b from-primary-950/40 via-surface-900 to-surface-950" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary-800/20 via-transparent to-transparent" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-accent-900/10 via-transparent to-transparent" />

        <div className="relative mx-auto max-w-7xl px-4 text-center sm:px-6">
          <div className="mx-auto max-w-3xl">
            <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl lg:text-6xl">
              The Global
              <span className="mt-1 block gradient-text">
                Combat Sports Rankings
              </span>
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-surface-300 sm:text-xl">
              ELO-based ranking system for BJJ, grappling, and combat sports athletes worldwide.
              Track your progress, compare with the best, and climb the leaderboard.
            </p>
            <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
              <Link href="/leaderboards" className="btn-primary px-8 py-3 text-base shadow-glow">
                View Rankings
              </Link>
              <Link
                href="/auth"
                className="btn rounded-xl border border-surface-600/50 px-8 py-3 text-base text-surface-200 hover:bg-white/5 hover:border-surface-500"
              >
                Create Account
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="border-b border-surface-200/50 bg-white py-14 dark:border-surface-700/30 dark:bg-surface-900">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-3xl font-bold text-primary-600 dark:text-primary-400">
                  {stat.value}
                </div>
                <div className="mt-1.5 text-sm text-surface-500 dark:text-surface-400">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-surface-900 dark:text-white">
              How It Works
            </h2>
            <p className="mx-auto mt-4 max-w-xl text-lg text-surface-500 dark:text-surface-400">
              A data-driven approach to ranking combat sports athletes globally.
            </p>
          </div>

          <div className="mt-16 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {features.map((feature) => (
              <div key={feature.title} className="card-hover text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-50 text-primary-600 dark:bg-primary-950/40 dark:text-primary-400">
                  {feature.icon}
                </div>
                <h3 className="mt-5 text-lg font-semibold text-surface-900 dark:text-white">
                  {feature.title}
                </h3>
                <p className="mt-2 text-sm text-surface-500 dark:text-surface-400">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative overflow-hidden py-20">
        <div className="absolute inset-0 bg-gradient-to-r from-primary-600 to-primary-800 dark:from-primary-700 dark:to-primary-900" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-accent-500/10 via-transparent to-transparent" />
        <div className="relative mx-auto max-w-7xl px-4 text-center sm:px-6">
          <h2 className="text-3xl font-bold text-white">
            Ready to track your ranking?
          </h2>
          <p className="mt-4 text-lg text-primary-100/80">
            Join the global combat sports community and see where you stand.
          </p>
          <Link
            href="/auth"
            className="mt-8 inline-flex items-center rounded-xl bg-white px-8 py-3 text-base font-medium text-primary-700 shadow-soft hover:bg-primary-50 transition-colors"
          >
            Get Started Free
          </Link>
        </div>
      </section>
    </div>
  );
}
