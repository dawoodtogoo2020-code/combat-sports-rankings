export function LogoMark({ className = "h-8 w-8" }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" fill="none" className={className} aria-hidden="true">
      {/* Outer ring — ranking circle motif */}
      <circle cx="16" cy="16" r="14" stroke="currentColor" strokeWidth="2" opacity="0.25" />
      {/* CS monogram — clean, professional */}
      <text
        x="16"
        y="21"
        textAnchor="middle"
        fill="currentColor"
        fontSize="14"
        fontWeight="800"
        fontFamily="Inter, system-ui, sans-serif"
        letterSpacing="-0.5"
      >
        CS
      </text>
      {/* Accent dot — ranking indicator */}
      <circle cx="26" cy="8" r="2.5" fill="currentColor" opacity="0.6" />
    </svg>
  );
}
