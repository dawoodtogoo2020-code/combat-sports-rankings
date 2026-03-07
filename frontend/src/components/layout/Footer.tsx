import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white dark:border-slate-800 dark:bg-surface-950">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Platform</h3>
            <ul className="mt-4 space-y-2">
              <li><Link href="/leaderboards" className="text-sm text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white">Leaderboards</Link></li>
              <li><Link href="/athletes" className="text-sm text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white">Athletes</Link></li>
              <li><Link href="/events" className="text-sm text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white">Events</Link></li>
              <li><Link href="/gyms" className="text-sm text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white">Gyms</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Sports</h3>
            <ul className="mt-4 space-y-2">
              <li><span className="text-sm text-slate-600 dark:text-slate-400">Brazilian Jiu-Jitsu</span></li>
              <li><span className="text-sm text-slate-600 dark:text-slate-400">No-Gi Grappling</span></li>
              <li><span className="text-sm text-slate-600 dark:text-slate-400">Wrestling</span></li>
              <li><span className="text-sm text-slate-600 dark:text-slate-400">MMA</span></li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Community</h3>
            <ul className="mt-4 space-y-2">
              <li><Link href="/social" className="text-sm text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white">Social Feed</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">About</h3>
            <ul className="mt-4 space-y-2">
              <li><span className="text-sm text-slate-600 dark:text-slate-400">How Rankings Work</span></li>
              <li><span className="text-sm text-slate-600 dark:text-slate-400">Contact</span></li>
            </ul>
          </div>
        </div>
        <div className="mt-8 border-t border-slate-200 pt-8 dark:border-slate-800">
          <p className="text-center text-sm text-slate-500 dark:text-slate-400">
            CS Rankings — The global combat sports ranking platform. ELO-based athlete rankings.
          </p>
        </div>
      </div>
    </footer>
  );
}
