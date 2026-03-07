export function LogoMark({ className = "h-8 w-8" }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" fill="none" className={className} aria-hidden="true">
      {/* Two flowing arcs — martial arts duality, enso-inspired */}
      <path
        d="M16 4C9.4 4 4 9.4 4 16c0 3.3 1.3 6.3 3.5 8.5"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
      <path
        d="M16 28c6.6 0 12-5.4 12-12 0-3.3-1.3-6.3-3.5-8.5"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
      <circle cx="12" cy="12" r="1.5" fill="currentColor" opacity="0.6" />
      <circle cx="20" cy="20" r="1.5" fill="currentColor" opacity="0.6" />
    </svg>
  );
}
