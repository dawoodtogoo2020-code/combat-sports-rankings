import Link from "next/link";
import { LogoMark } from "@/components/ui/Logo";

export function Footer() {
  return (
    <footer className="border-t border-surface-200/50 bg-white dark:border-surface-700/30 dark:bg-surface-950">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          <div>
            <h3 className="text-sm font-semibold text-surface-900 dark:text-white">Platform</h3>
            <ul className="mt-4 space-y-2">
              <li><Link href="/leaderboards" className="text-sm text-surface-500 hover:text-surface-900 dark:text-surface-400 dark:hover:text-white transition-colors">Leaderboards</Link></li>
              <li><Link href="/athletes" className="text-sm text-surface-500 hover:text-surface-900 dark:text-surface-400 dark:hover:text-white transition-colors">Athletes</Link></li>
              <li><Link href="/events" className="text-sm text-surface-500 hover:text-surface-900 dark:text-surface-400 dark:hover:text-white transition-colors">Events</Link></li>
              <li><Link href="/gyms" className="text-sm text-surface-500 hover:text-surface-900 dark:text-surface-400 dark:hover:text-white transition-colors">Gyms</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-surface-900 dark:text-white">Sports</h3>
            <ul className="mt-4 space-y-2">
              <li><span className="text-sm text-surface-500 dark:text-surface-400">Brazilian Jiu-Jitsu</span></li>
              <li><span className="text-sm text-surface-500 dark:text-surface-400">No-Gi Grappling</span></li>
              <li><span className="text-sm text-surface-500 dark:text-surface-400">Wrestling</span></li>
              <li><span className="text-sm text-surface-500 dark:text-surface-400">MMA</span></li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-surface-900 dark:text-white">Community</h3>
            <ul className="mt-4 space-y-2">
              <li><Link href="/social" className="text-sm text-surface-500 hover:text-surface-900 dark:text-surface-400 dark:hover:text-white transition-colors">Social Feed</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-surface-900 dark:text-white">About</h3>
            <ul className="mt-4 space-y-2">
              <li><span className="text-sm text-surface-500 dark:text-surface-400">How Rankings Work</span></li>
              <li><span className="text-sm text-surface-500 dark:text-surface-400">Contact</span></li>
            </ul>
          </div>
        </div>
        <div className="mt-8 flex items-center justify-between border-t border-surface-200/50 pt-8 dark:border-surface-700/30">
          <div className="flex items-center gap-2 text-surface-400">
            <LogoMark className="h-5 w-5" />
            <span className="text-sm">CS Rankings</span>
          </div>
          <p className="text-sm text-surface-400">
            The global combat sports ranking platform
          </p>
        </div>
      </div>
    </footer>
  );
}
