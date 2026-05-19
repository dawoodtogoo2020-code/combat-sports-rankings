"""
ADCC scraper — Abu Dhabi Combat Club submission wrestling.

adcombat.com is a WordPress site. The events archive lives at /adcc-events/ and
individual event pages are at /adcc-events/{slug}/. Like IBJJF, ADCC publishes
placement data per weight class (gold/silver/bronze medals as <img> tags inside
<ul>/<li> lists under <h4> division headings), not bracket-by-bracket matches.

We synthesize pseudo-matches from podium ordering. ADCC events are always elite
tier and no-gi.
"""

import logging
import re
from datetime import date

from bs4 import BeautifulSoup

from app.ingestion.base import BaseIngester, ImportedEvent, ImportedAthlete
from app.ingestion.http_client import ScraperHttpClient
from app.ingestion.scrapers.parsers import (
    build_pseudo_matches_from_placements,
    extract_name_parts,
    log_empty_parse,
    parse_date,
    select_first,
    text_of,
)

logger = logging.getLogger(__name__)

BASE_URL = "https://adcombat.com"
EVENTS_INDEX = f"{BASE_URL}/adcc-events/"

EVENT_URL_RE = re.compile(r"/adcc-events/([^/]+)/?$")
MEDAL_RE = re.compile(r"(gold|silver|bronze)[\s\-_]*medal", re.IGNORECASE)


class AdccIngester(BaseIngester):
    source_name = "adcc"

    def __init__(self, http_client: ScraperHttpClient):
        self.http = http_client

    async def fetch_events(self, **kwargs) -> list[ImportedEvent]:
        events: list[ImportedEvent] = []

        html = await self.http.get_html(EVENTS_INDEX)
        if not html:
            logger.warning(f"Could not fetch ADCC events index at {EVENTS_INDEX}")
            return events

        soup = BeautifulSoup(html, "lxml")
        seen: set[str] = set()

        # WordPress archive — every event is an anchor linking to /adcc-events/{slug}/
        for link in soup.find_all("a", href=True):
            href = link["href"]
            match = EVENT_URL_RE.search(href)
            if not match:
                continue
            slug = match.group(1)
            if slug in seen or slug == "":
                continue
            seen.add(slug)

            name = link.get_text(strip=True) or slug.replace("-", " ").title()
            if len(name) < 5 or len(name) > 200:
                continue

            # Pull a year from the slug if possible
            year_match = re.search(r"(20\d{2}|19\d{2})", slug)
            event_year = int(year_match.group(1)) if year_match else date.today().year
            event_date = date(event_year, 1, 1)

            # Try to find a date in surrounding markup
            parent = link.parent
            if parent:
                date_text = text_of(select_first(parent, "time", ".date", ".event-date"))
                parsed = parse_date(date_text)
                if parsed:
                    event_date = parsed

            events.append(ImportedEvent(
                name=name,
                event_date=event_date,
                organizer="ADCC",
                tier="elite",
                is_gi=False,
                is_nogi=True,
                source="adcc",
                source_id=slug,
                source_url=href if href.startswith("http") else f"{BASE_URL}{href}",
            ))

        if not events:
            log_empty_parse("adcc", EVENTS_INDEX, html)
        logger.info(f"Found {len(events)} ADCC events")
        return events

    async def fetch_event_results(self, event_id: str) -> ImportedEvent | None:
        """ADCC events publish placements per weight class as <ul>/<li> under <h4>."""
        url = f"{BASE_URL}/adcc-events/{event_id}/"
        html = await self.http.get_html(url)
        if not html:
            logger.warning(f"Could not fetch ADCC event page {url}")
            return None

        soup = BeautifulSoup(html, "lxml")
        title = text_of(
            select_first(soup, "h1.entry-title", "h1.post-title", "h1", ".entry-title"),
            f"ADCC {event_id}",
        )

        event = ImportedEvent(
            name=title,
            event_date=date.today(),
            organizer="ADCC",
            tier="elite",
            is_gi=False,
            is_nogi=True,
            source="adcc",
            source_id=event_id,
            source_url=url,
        )

        # Try to extract event date from common WordPress patterns
        date_node = select_first(soup, "time.entry-date", "time[datetime]", ".post-date time")
        if date_node:
            dt = date_node.get("datetime") or date_node.get_text(strip=True)
            parsed = parse_date(dt or "")
            if parsed:
                event.event_date = parsed

        # Article body — limit search to the post content
        body = select_first(soup, ".entry-content", ".post-content", "article", "main") or soup

        # Walk each <h4>/<h3> as a division header, collect placers from the following <ul>
        headings = body.select("h2, h3, h4, h5")
        if not headings:
            log_empty_parse("adcc", url, html)
            return event

        for heading in headings:
            div_label = heading.get_text(" ", strip=True)
            if not div_label or len(div_label) > 200:
                continue
            # Filter to looks-like-weight-class headers
            looks_like_division = bool(
                re.search(r"kg|lbs|under|over|absolute|open\s+weight|female|male|men|women|division|weight", div_label, re.IGNORECASE)
            )
            if not looks_like_division:
                continue

            gender = "female" if re.search(r"female|women", div_label, re.IGNORECASE) else "male"

            # Look for the next <ul> or table after the heading
            list_node = heading.find_next(["ul", "ol", "table"])
            if not list_node:
                continue

            placers: list[ImportedAthlete] = []
            items = list_node.find_all(["li", "tr"]) if list_node.name in {"ul", "ol", "table"} else []
            for item in items:
                text = item.get_text(" ", strip=True)
                if not text:
                    continue
                # Strip medal alt-text artifacts
                text = MEDAL_RE.sub("", text).strip()
                # Strip leading rank markers
                text = re.sub(r"^\s*(\d+(?:st|nd|rd|th)?[\.\)\s-]+)", "", text)
                # Often format: "Name (Country) — Team"
                name_part = re.split(r"[—\-\(]", text, maxsplit=1)[0].strip()
                first, last = extract_name_parts(name_part)
                if first == "Unknown" or not last:
                    continue
                placers.append(ImportedAthlete(
                    first_name=first,
                    last_name=last,
                    gender=gender,
                ))
                if len(placers) >= 4:  # gold/silver/2x bronze
                    break

            event.matches.extend(build_pseudo_matches_from_placements(
                placers,
                division_name=div_label,
                is_gi=False,
            ))

        if not event.matches:
            log_empty_parse("adcc", url, html)
        logger.info(f"ADCC event {event_id}: synthesized {len(event.matches)} pseudo-matches from placements")
        return event
