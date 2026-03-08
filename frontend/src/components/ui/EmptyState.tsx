import Link from "next/link";

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  actionLabel?: string;
  actionHref?: string;
}

/* Circular decorative motif — subtle, combat-sports-inspired */
function DefaultIcon() {
  return (
    <svg viewBox="0 0 64 64" className="h-16 w-16 text-surface-300 dark:text-surface-600" fill="none" aria-hidden="true">
      <circle cx="32" cy="32" r="28" stroke="currentColor" strokeWidth="1.5" strokeDasharray="4 4" opacity="0.5" />
      <circle cx="32" cy="32" r="18" stroke="currentColor" strokeWidth="1" opacity="0.3" />
      <circle cx="32" cy="32" r="4" fill="currentColor" opacity="0.2" />
    </svg>
  );
}

export function EmptyState({ icon, title, description, actionLabel, actionHref }: EmptyStateProps) {
  return (
    <div className="card py-16 text-center">
      <div className="mx-auto mb-5 flex items-center justify-center">
        {icon || <DefaultIcon />}
      </div>
      <h3 className="text-lg font-semibold text-surface-900 dark:text-white">
        {title}
      </h3>
      <p className="mx-auto mt-2 max-w-sm text-sm text-surface-500 dark:text-surface-400">
        {description}
      </p>
      {actionLabel && actionHref && (
        <Link href={actionHref} className="btn-primary mt-6 inline-flex text-sm">
          {actionLabel}
        </Link>
      )}
    </div>
  );
}

/* Pre-built icons for specific sections */
export function AthletesIcon() {
  return (
    <svg viewBox="0 0 64 64" className="h-16 w-16 text-surface-300 dark:text-surface-600" fill="none" aria-hidden="true">
      <circle cx="32" cy="22" r="10" stroke="currentColor" strokeWidth="1.5" opacity="0.5" />
      <path d="M14 54c0-10 8-18 18-18s18 8 18 18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" opacity="0.4" />
      <circle cx="32" cy="32" r="30" stroke="currentColor" strokeWidth="1" strokeDasharray="3 6" opacity="0.2" />
    </svg>
  );
}

export function RankingsIcon() {
  return (
    <svg viewBox="0 0 64 64" className="h-16 w-16 text-surface-300 dark:text-surface-600" fill="none" aria-hidden="true">
      <rect x="10" y="34" width="12" height="20" rx="2" stroke="currentColor" strokeWidth="1.5" opacity="0.4" />
      <rect x="26" y="20" width="12" height="34" rx="2" stroke="currentColor" strokeWidth="1.5" opacity="0.5" />
      <rect x="42" y="28" width="12" height="26" rx="2" stroke="currentColor" strokeWidth="1.5" opacity="0.35" />
      <circle cx="32" cy="12" r="5" stroke="currentColor" strokeWidth="1" opacity="0.3" />
    </svg>
  );
}

export function EventsIcon() {
  return (
    <svg viewBox="0 0 64 64" className="h-16 w-16 text-surface-300 dark:text-surface-600" fill="none" aria-hidden="true">
      <rect x="10" y="14" width="44" height="40" rx="4" stroke="currentColor" strokeWidth="1.5" opacity="0.4" />
      <line x1="10" y1="26" x2="54" y2="26" stroke="currentColor" strokeWidth="1" opacity="0.3" />
      <line x1="22" y1="10" x2="22" y2="18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" opacity="0.5" />
      <line x1="42" y1="10" x2="42" y2="18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" opacity="0.5" />
      <circle cx="32" cy="40" r="6" stroke="currentColor" strokeWidth="1" opacity="0.3" />
    </svg>
  );
}

export function GymsIcon() {
  return (
    <svg viewBox="0 0 64 64" className="h-16 w-16 text-surface-300 dark:text-surface-600" fill="none" aria-hidden="true">
      <rect x="16" y="22" width="32" height="30" rx="3" stroke="currentColor" strokeWidth="1.5" opacity="0.4" />
      <path d="M16 22L32 10l16 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.5" />
      <rect x="26" y="38" width="12" height="14" rx="1.5" stroke="currentColor" strokeWidth="1" opacity="0.3" />
    </svg>
  );
}

export function SocialIcon() {
  return (
    <svg viewBox="0 0 64 64" className="h-16 w-16 text-surface-300 dark:text-surface-600" fill="none" aria-hidden="true">
      <rect x="8" y="12" width="36" height="28" rx="4" stroke="currentColor" strokeWidth="1.5" opacity="0.4" />
      <path d="M8 36l10 10v-10" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" opacity="0.3" />
      <rect x="20" y="24" width="28" height="22" rx="4" stroke="currentColor" strokeWidth="1.5" opacity="0.35" />
      <line x1="26" y1="32" x2="42" y2="32" stroke="currentColor" strokeWidth="1" opacity="0.25" />
      <line x1="26" y1="38" x2="36" y2="38" stroke="currentColor" strokeWidth="1" opacity="0.2" />
    </svg>
  );
}
