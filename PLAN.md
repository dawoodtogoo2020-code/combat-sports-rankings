# Combat Sports Rankings — Improvement Plan

## Design Philosophy

Not neon-cyber. Think: **twilight over a dojo garden.**
Rich depth like oil paint on dark canvas. Japanese-inspired negative space.
Organic warmth within a dark, focused interface. Every element intentional.

---

## Phase 1: Theme & Visual Foundation

### 1a. Color System Overhaul (`tailwind.config.ts` + `globals.css`)

Replace the current blue brand palette with a layered, organic palette:

- **Primary**: Deep violet/plum tones (like sky 30 min after sunset)
  - Range from soft lavender (highlights) to deep purple-black (depth)
- **Base/Surface**: Warm dark grays with slight violet undertone (ink on handmade paper)
- **Accent**: Dusty rose / soft magenta (cherry blossom, not laser)
- **Secondary**: Muted brass gold for special elements (ranks, badges)
- **Success**: Moss green (earthy, not neon)
- **Danger**: Clay red (warm, not alarm)
- **Muted text**: Warm slate with slight violet cast

Update CSS variables for both light and dark modes.
Rework `.card`, `.badge`, `.btn`, `.input` utility classes.
Add subtle gradient utilities and soft glow/shadow classes.

### 1b. Typography Refinement

- Keep Inter but refine weight usage (lighter body, bolder headings)
- Increase line-height for breathing room
- Adjust letter-spacing for headings (slight tracking)

### 1c. Logo & Favicon

Create an SVG logo mark:
- Abstract, minimal — could suggest a guard position or grappling form
- Works at favicon size (16px) and full brand size
- Organic curves, not hard geometric
- Update in Navbar and as favicon in layout.tsx

---

## Phase 2: Navbar & Hero Section

### 2a. Navbar Polish
- Refine spacing and visual weight
- Subtle gradient border-bottom or atmospheric shadow
- Smooth mobile menu with gentle transitions
- Active page indicator (understated, like a soft underline)

### 2b. Hero Section Redesign
- Replace current gradient with atmospheric, layered background
  (deep-to-deeper gradient with subtle radial warmth)
- Refine typography hierarchy — hero title with presence, subtitle with softness
- Stats row: breathe more, subtle entrance feel
- Feature cards below: organic card styling with gentle hover states
- More whitespace between sections

---

## Phase 3: Component Polish (cards, tables, states)

### 3a. Card System
- More generous padding and rounded corners
- Subtle border with low-opacity violet tint
- Soft shadow that feels like depth, not elevation
- Hover: gentle scale + shadow shift (organic timing ~300ms ease)

### 3b. Skeleton Loaders
- Create a reusable `<Skeleton />` component
- Soft pulse animation with violet-tinted placeholder blocks
- Apply to: athlete cards, leaderboard rows, event cards, profile sections

### 3c. Empty States
- Thoughtful empty state messages with subtle illustrations
- "No athletes found" with a soft visual, not just text

### 3d. Rating Indicators
- ↑ moss green with gentle upward accent
- ↓ clay red with subtle downward accent
- Trend sparklines: thin, organic line (not blocky charts)

---

## Phase 4: Leaderboard / Rankings Page

- Add filter bar: weight class, belt rank, gi/nogi, country
  - Pill-style filter chips with gentle active states
- Sort controls with clear active indicator
- Trend column: small sparkline or arrow with color
- Rank medals: refined with muted gold/silver/bronze tones
- Better pagination with page numbers
- Smooth filter transitions

---

## Phase 5: Athlete Profile Page

- Refined header layout with more breathing room
- Rating history: replace bar chart with smooth line chart (organic curve)
  using a lightweight approach (CSS/SVG, or recharts which is already installed)
- Win/loss breakdown: subtle donut or horizontal bar
- Submission vs decision breakdown
- Recent matches table with better spacing
- Weight division and belt rank display

---

## Phase 6: Mobile Optimization

- Test and fix all pages at 320px-768px
- Navbar: full-screen overlay menu with smooth animation
- Leaderboard: horizontal scroll or stacked card view on mobile
- Filter bar: horizontally scrollable pill row
- Cards: full-width with proper touch targets (min 44px)
- Tables: card-based layout on small screens instead of squeezed columns

---

## Phase 7: Remaining Page Polish

- **Events page**: better tier badges, card layout refinement
- **Event detail**: atmospheric header, cleaner match results
- **Gyms page**: refined cards with member preview
- **Gym detail**: better athlete list layout
- **Social page**: refined post cards, better compose area
- **Auth page**: atmospheric background, refined form
- **Admin page**: cleaner dashboard cards, better data tables

---

## Phase 8: Push & Deploy

- Verify build passes (static export)
- Commit all changes
- Push to GitHub
- Cloudflare Pages auto-deploys
- Verify live site

---

## Files Changed (estimated)

| File | Changes |
|------|---------|
| `tailwind.config.ts` | New color palette, spacing, fonts |
| `globals.css` | Reworked variables, components, new utilities |
| `layout.tsx` | Logo/favicon, meta updates |
| `Navbar.tsx` | Visual polish, mobile menu |
| `Footer.tsx` | Updated styling |
| `page.tsx` (home) | Hero redesign, feature cards |
| `leaderboards/page.tsx` | Filters, trends, polish |
| `athletes/page.tsx` | Card polish, empty states |
| `athletes/[id]/page.tsx` | Profile overhaul, charts |
| `events/page.tsx` | Card polish |
| `events/[id]/page.tsx` | Detail polish |
| `gyms/page.tsx` | Card polish |
| `gyms/[id]/page.tsx` | Detail polish |
| `social/page.tsx` | Post card polish |
| `auth/page.tsx` | Form polish |
| `admin/page.tsx` | Dashboard polish |
| New: `components/ui/Skeleton.tsx` | Skeleton loader component |

No backend changes in this pass. All improvements are frontend visual/UX.
