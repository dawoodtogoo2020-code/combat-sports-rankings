"""
IBJJF scraper — International Brazilian Jiu-Jitsu Federation.

IBJJF publishes results in two places:
  - ibjjf.com/results — index of championships, links to detail pages
  - ibjjfdb.com/ChampionshipResults/{id}/PublicResults — actual placement data

They publish placement-only data (gold/silver/bronze per weight class), not match
brackets. We synthesize pseudo-matches from podium ordering (see
`build_pseudo_matches_from_placements`). Strictly respects robots.txt.
"""

import logging
import re
from datetime import date

from bs4 import BeautifulSoup

from app.ingestion.base import BaseIngester, ImportedEvent, ImportedAthlete
from app.ingestion.http_client import ScraperHttpClient
from app.ingestion.scrapers.parsers import (
    build_pseudo_matches_from_placements,
    log_empty_parse,
    parse_date,
    parse_division,
    select_any,
    select_first,
    text_of,
)

logger = logging.getLogger(__name__)

INDEX_URL = "https://ibjjf.com/results"
DB_BASE = "https://www.ibjjfdb.com"


class IbjjfIngester(BaseIngester):
    source_name = "ibjjf"

    def __init__(self, http_client: ScraperHttpClient):
        self.http = http_client

    async def fetch_events(self, **kwargs) -> list[ImportedEvent]:
        """Fetch IBJJF championship index. Returns events with `source_id` set to the
        ChampionshipResults numeric ID (when available) or the legacy slug.
        """
        events: list[ImportedEvent] = []

        # Compliance check — IBJJF historically blocks some bot UAs
        if await self.http.compliance.get_robots_status(INDEX_URL) == "disallowed":
            logger.info("IBJJF robots.txt disallows /results — skipping")
            return events

        html = await self.http.get_html(INDEX_URL)
        if not html:
            logger.warning("Could not fetch IBJJF results index")
            return events

        soup = BeautifulSoup(html, "lxml")

        # The index page is mostly anchor-driven: each championship is a link.
        # Two URL forms exist:
        #   - https://www.ibjjfdb.com/ChampionshipResults/{id}/PublicResults (modern)
        #   - https://ibjjf.com/events/results/{year}-{slug} (legacy, pre-2012)
        modern_re = re.compile(r"ibjjfdb\.com/ChampionshipResults/(\d+)/PublicResults", re.IGNORECASE)
        legacy_re = re.compile(r"/events/results/(\d{4})-([\w-]+)", re.IGNORECASE)

        seen_ids: set[str] = set()
        for link in soup.find_all("a", href=True):
            href: str = link["href"]
            name = link.get_text(strip=True)
            if not name or len(name) > 200:
                continue

            event_id: str | None = None
            event_year: int | None = None

            modern = modern_re.search(href)
            if modern:
                event_id = modern.group(1)
                source_url = f"{DB_BASE}/ChampionshipResults/{event_id}/PublicResults"
            else:
                legacy = legacy_re.search(href)
                if legacy:
                    event_id = f"legacy-{legacy.group(1)}-{legacy.group(2)}"
                    event_year = int(legacy.group(1))
                    source_url = href if href.startswith("http") else f"https://ibjjf.com{href}"
                else:
                    continue

            if event_id in seen_ids:
                continue
            seen_ids.add(event_id)

            # Year hint from surrounding text (look at parent context)
            if event_year is None:
                parent_text = link.parent.get_text(" ", strip=True) if link.parent else ""
                year_match = re.search(r"\b(20\d{2}|19\d{2})\b", parent_text)
                if year_match:
                    event_year = int(year_match.group(1))

            event_date = date(event_year, 1, 1) if event_year else date.today()

            lname = name.lower()
            if "world" in lname and "master" not in lname:
                tier = "elite"
            elif any(t in lname for t in ("pan", "european", "asian")):
                tier = "national"
            elif "open" in lname:
                tier = "regional"
            else:
                tier = "regional"

            events.append(ImportedEvent(
                name=name,
                event_date=event_date,
                organizer="IBJJF",
                tier=tier,
                is_gi=True,
                source="ibjjf",
                source_id=event_id,
                source_url=source_url,
            ))

        if not events:
            log_empty_parse("ibjjf", INDEX_URL, html)
        logger.info(f"Found {len(events)} IBJJF championships")
        return events

    async def fetch_event_results(self, event_id: str) -> ImportedEvent | None:
        """Fetch placement data for an IBJJF championship and synthesize pseudo-matches."""
        if event_id.startswith("legacy-"):
            logger.info(f"IBJJF legacy event {event_id} — placement data not available, skipping")
            return None

        url = f"{DB_BASE}/ChampionshipResults/{event_id}/PublicResults"
        html = await self.http.get_html(url)
        if not html:
            logger.warning(f"Could not fetch IBJJF results for event {event_id}")
            return None

        soup = BeautifulSoup(html, "lxml")
        event_name = text_of(
            select_first(soup, "h1", ".championship-name", ".event-title", "title"),
            f"IBJJF Championship {event_id}",
        )

        event = ImportedEvent(
            name=event_name,
            event_date=date.today(),
            organizer="IBJJF",
            tier="elite",
            is_gi=True,
            source="ibjjf",
            source_id=event_id,
            source_url=url,
        )

        # IBJJFDB uses a placement structure: each division has a section with ranked athletes.
        # Selectors are best-effort with multiple fallbacks.
        divisions = select_any(
            soup,
            ".division-results",
            ".weight-class",
            "[data-division]",
            "section.results",
            ".bracket",
        )

        # If no structured divisions, fall back to heading-keyed parsing
        if not divisions:
            for heading in soup.select("h2, h3, h4"):
                div_label = heading.get_text(strip=True)
                if not div_label or len(div_label) > 200:
                    continue
                div_info = parse_division(div_label)

                placers: list[ImportedAthlete] = []
                for sibling in heading.find_all_next(limit=80):
                    if sibling.name in {"h2", "h3", "h4"} and sibling is not heading:
                        break
                    if sibling.name not in {"li", "tr", "p", "div"}:
                        continue
                    txt = sibling.get_text(" ", strip=True)
                    if not txt:
                        continue
                    # Rank prefix is common: "1. John Doe — Academy"
                    rank_match = re.match(r"^\s*(\d+)(?:st|nd|rd|th)?[\.\)\s-]+(.+)", txt)
                    if not rank_match:
                        continue
                    name_part = rank_match.group(2).split("—")[0].split("-")[0].strip()
                    parts = name_part.split()
                    if len(parts) < 2:
                        continue
                    placers.append(ImportedAthlete(
                        first_name=parts[0],
                        last_name=" ".join(parts[1:]),
                        gender=div_info.get("gender", "male"),
                        belt_rank=div_info.get("belt"),
                    ))
                    if len(placers) >= 6:
                        break

                event.matches.extend(build_pseudo_matches_from_placements(
                    placers,
                    division_name=div_label,
                    is_gi=div_info.get("is_gi", True),
                ))
        else:
            for div in divisions:
                div_label = text_of(select_first(div, ".division-name", ".weight-class-name", "h3", "h4"))
                div_info = parse_division(div_label) if div_label else {}
                placers: list[ImportedAthlete] = []
                for row in select_any(div, ".placement", ".result-row", "li", "tr"):
                    txt = row.get_text(" ", strip=True)
                    rank_match = re.match(r"^\s*(\d+)(?:st|nd|rd|th)?[\.\)\s-]+(.+)", txt)
                    if not rank_match:
                        continue
                    name_part = rank_match.group(2).split("—")[0].split("-")[0].strip()
                    parts = name_part.split()
                    if len(parts) < 2:
                        continue
                    placers.append(ImportedAthlete(
                        first_name=parts[0],
                        last_name=" ".join(parts[1:]),
                        gender=div_info.get("gender", "male"),
                        belt_rank=div_info.get("belt"),
                    ))
                    if len(placers) >= 6:
                        break

                event.matches.extend(build_pseudo_matches_from_placements(
                    placers,
                    division_name=div_label or None,
                    is_gi=div_info.get("is_gi", True),
                ))

        if not event.matches:
            log_empty_parse("ibjjf", url, html)
        logger.info(f"IBJJF event {event_id}: synthesized {len(event.matches)} pseudo-matches from placements")
        return event
