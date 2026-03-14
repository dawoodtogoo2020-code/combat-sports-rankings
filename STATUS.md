# Combat Sports Rankings — Project Status

**Last updated:** 2026-03-14

## What's Done

### Frontend (Next.js 15 + Tailwind, static export)

| Page | Status | Notes |
|------|--------|-------|
| Home | Done | Hero, features, stats icons, CTA sections |
| Athletes | Done | Search, grid of cards, ELO/record display |
| Athlete Detail | Done | Profile header, full stats panel, SVG rating history chart, win/loss bar |
| Leaderboards | Done | Global + country tabs, gender/format filters, pagination, rank badges, trend indicators |
| Events | Done | Tier-based badge styling, search, date formatting |
| Event Detail | Done | Header with tier/format badges, match results list with athlete names & ELO changes |
| Gyms | Done | Search, member count, avg rating cards |
| Gym Detail | Done | Header, stats, ranked athlete list linking to profiles |
| Social Feed | Done | Posts with type badges, media upload, comments, likes, hashtags |
| Auth | Done | Register/login forms, password validation, error handling |
| Admin | Done | Dashboard stats, athlete ELO adjustment, user list, CSV import, audit log, data sources, scrape controls |

**Cross-cutting features:**
- Dark/light mode toggle
- Responsive layouts (mobile-first)
- Loading skeleton placeholders
- Empty states with guidance messages
- JWT auth with auto-refresh (2 min before expiry)
- Typed API client with all endpoints (`lib/api.ts`)
- Graceful fallback when backend is unreachable (shows empty states, no crashes)
- SPA fallback via `_redirects` for Cloudflare Pages
- 100 pre-rendered detail page IDs for static export

### Backend (FastAPI + PostgreSQL)

| Module | Status | Notes |
|--------|--------|-------|
| Auth | Done | JWT access+refresh tokens, bcrypt, register/login/me |
| Athletes API | Done | List (search, filter, paginate), get, rating history |
| Events API | Done | List, get, matches with athlete names |
| Gyms API | Done | List, get, gym athletes |
| Leaderboards API | Done | Global + country rankings, gender/format filters |
| Social API | Done | Feed, create post, like toggle, comments |
| Admin API | Done | Dashboard, ELO adjust, recalculate, merge duplicates, verify/reject matches, moderate posts, audit log, data sources, scrape triggers, scrape logs |
| Upload API | Done | Multipart media upload with progress |
| ELO Engine | Done | K-factor modifiers (tier, rating, newness), outcome multipliers, belt upset bonus, CP calculation |
| CSV Ingestion | Done | Parse and import match results from CSV |
| Rate Limiting | Done | 30/min on most endpoints |
| Database Models | Done | Users, athletes, matches, events, gyms, social, ratings, audit logs, data sources, scrape logs |
| Seed Data | Done | 5 sports, IBJJF+ADCC weight classes, 10 gyms, 60+ athletes, 150+ matches, admin user |

### Data Ingestion System (NEW — built this session)

| Component | Status | Notes |
|-----------|--------|-------|
| Compliance layer | Done | robots.txt checking, rate limiting (2 req/s per domain), user-agent identification |
| HTTP client | Done | Wraps httpx with compliance enforcement on every request |
| Shared parsers | Done | Name extraction, match outcome normalization, division parsing, date parsing, country codes |
| SmoothComp scraper | Done | JSON API + HTML fallback for BJJ tournament platform |
| AJP scraper | Done | Abu Dhabi Jiu-Jitsu Pro tour results |
| IBJJF scraper | Done | International BJJ Federation (strict robots.txt respect — skips if blocked) |
| NAGA scraper | Done | North American Grappling Association (CSV + HTML) |
| Grappling Industries scraper | Done | Round-robin tournament results |
| ADCC scraper | Done | Abu Dhabi Combat Club submission wrestling |
| Import service | Done | Normalizes scraped data into DB: creates athletes, events, matches, calculates ELO |
| Orchestrator | Done | Coordinates multi-source scraping, creates ScrapeLog entries, handles errors |
| Admin endpoints | Done | `POST /scrape/all`, `POST /scrape/{source}`, `GET /scrape/logs`, `GET /scrape/sources` |
| Celery tasks | Done | Background workers for scraping, daily beat schedule, retry logic |
| ScrapeLog model | Done | Tracks every run: status, events found, matches imported, errors |

**Compliance features:**
- Checks and caches robots.txt for each domain before scraping
- Rate-limits to 2 requests/second per domain (configurable)
- Identifies as `CombatSportsRankingsBot/1.0` in User-Agent
- If robots.txt disallows access, the source is skipped entirely
- All scrape runs are logged in `scrape_logs` table for auditability

### Deployment Configuration (NEW — built this session)

| File | Purpose |
|------|---------|
| `railway.toml` | Railway deployment config (Dockerfile build, health check) |
| `Dockerfile` | Python 3.12-slim, non-root user, gunicorn+uvicorn |
| `entrypoint.sh` | Runs alembic migrations, optional seed, starts server |
| `.env.example` | Template for all required environment variables |
| `alembic/env.py` | Reads `DATABASE_URL_SYNC` from env for production migrations |

---

## What Needs to Be Done

### Critical (Required for Launch)

1. **Deploy the backend to Railway** — Everything is configured. Steps:
   - Create a Railway project
   - Add PostgreSQL plugin (Railway auto-injects `DATABASE_URL`)
   - Add Redis plugin (Railway auto-injects `REDIS_URL`)
   - Connect GitHub repo, set root directory to `backend/`
   - Set env vars: `JWT_SECRET_KEY`, `CORS_ORIGINS`, `FRONTEND_URL`, `DATABASE_URL_SYNC`
   - Set `RUN_SEED=true` for first deploy, then remove it
   - After deploy: update Cloudflare Pages env var `NEXT_PUBLIC_API_URL` to the Railway URL

2. **Generate Alembic migration** — The scrape_logs table and any schema changes need a migration:
   ```bash
   cd backend
   alembic revision --autogenerate -m "add scrape_logs table"
   alembic upgrade head
   ```

3. **Set Cloudflare Pages `NEXT_PUBLIC_API_URL`** — Point frontend to the live backend URL.

### Important (Should have before public use)

4. **Run initial scrape** — After deploying, trigger `POST /api/v1/admin/scrape/all` to populate real competition data from all 6 sources.

5. **Start Celery worker for background scraping** — Add a second Railway service (or use `railway.toml` worker):
   ```bash
   celery -A app.celery_app worker --loglevel=info
   celery -A app.celery_app beat --loglevel=info
   ```

6. **Test scrapers against live sites** — The scrapers use generic CSS selectors. Each source site has a different HTML structure; the selectors may need tuning after first real scrapes.

7. **Add more seed athletes and matches** — Current 60 athletes and 150 matches is thin. The scraping system should populate real data.

8. **Testing** — No test suite exists yet.
   - Backend: pytest with async fixtures
   - Frontend: Jest + React Testing Library

### Nice to Have

9. **Error boundaries** — React error boundaries for component-level failure isolation.

10. **Search improvements** — Current search is basic `ILIKE`. Could add full-text search.

11. **Caching** — Redis cache headers for leaderboards and athlete lists.

12. **Email verification** — Registration works but no email flow.

13. **Athlete claiming** — Let users claim profiles (`is_claimed` exists in schema but no UI).

14. **Match verification queue** — Admin UI for a dedicated verify/reject queue view.

15. **Notifications** — WebSocket or polling for ranking changes.

16. **SEO** — `generateMetadata` with static data or server rendering.

17. **Analytics** — Plausible, Umami, or Cloudflare Web Analytics.

---

## Architecture Summary

```
Frontend (Cloudflare Pages)          Backend (Railway)
┌─────────────────────────┐         ┌──────────────────────────────┐
│ Next.js 15 static export│  HTTP   │ FastAPI (async)               │
│ React 19 + Tailwind     │ ──────> │ SQLAlchemy + PostgreSQL       │
│ JWT tokens in           │         │ ELO engine                    │
│ localStorage            │         │ Rate limiting (SlowAPI)       │
└─────────────────────────┘         │ Celery + Redis (bg scraping)  │
                                    │ 6 scrapers + compliance layer │
                                    └──────────────────────────────┘
```

## Data Sources

| Source | URL | Method | Notes |
|--------|-----|--------|-------|
| SmoothComp | smoothcomp.com | JSON API + HTML | Major BJJ tournament platform |
| AJP Tour | ajptour.com | JSON API + HTML | Abu Dhabi Pro tour |
| IBJJF | ibjjf.com | HTML | Strict robots.txt respected |
| NAGA | nagafighter.com | CSV + HTML | North American events |
| Grappling Industries | grapplingindustries.com | HTML | Round-robin tournaments |
| ADCC | adcombat.com | HTML tables | Elite no-gi events |

## Key Credentials (Development Only)
- Admin login: `admin@csrankings.com` / `admin123456`
- Default API: `http://localhost:8000/api/v1`
