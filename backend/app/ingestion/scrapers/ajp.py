"""
AJP Tour scraper — Abu Dhabi Jiu-Jitsu Pro tour.

ajptour.com renders the events listing via client-side JS hydration, which means
pure httpx + BeautifulSoup will often see an empty page. We try multiple paths:

  1. JSON API endpoints (best — stable, no scraping needed)
  2. The federation events page at /federation/1/events (sometimes server-rendered)
  3. The /en/events fallback

When all three fail, we log clearly so production can switch to a Playwright-based
fetcher without guessing what broke.

Individual event URLs follow /en/event/{numeric_id} when available.
"""

import logging
import re
from datetime import date

from bs4 import BeautifulSoup

from app.ingestion.base import BaseIngester, ImportedEvent, ImportedMatch, ImportedAthlete
from app.ingestion.http_client import ScraperHttpClient
from app.ingestion.scrapers.parsers import (
    extract_name_parts,
    log_empty_parse,
    parse_date,
    parse_division,
    parse_match_outcome,
    select_any,
    select_first,
    text_of,
)

logger = logging.getLogger(__name__)

BASE_URL = "https://ajptour.com"
API_CANDIDATES = [
    f"{BASE_URL}/api/v1/events?status=past",
    f"{BASE_URL}/api/events?status=past",
    f"{BASE_URL}/federation/1/events.json",
]
HTML_CANDIDATES = [
    f"{BASE_URL}/federation/1/events",
    f"{BASE_URL}/en/events",
]
EVENT_LINK_RE = re.compile(r"/en/event/(\d+)", re.IGNORECASE)


class AjpIngester(BaseIngester):
    source_name = "ajp"

    def __init__(self, http_client: ScraperHttpClient):
        self.http = http_client

    async def fetch_events(self, **kwargs) -> list[ImportedEvent]:
        events: list[ImportedEvent] = []

        # 1) Try JSON APIs in order
        for api_url in API_CANDIDATES:
            json_data = await self.http.get_json(api_url)
            if json_data:
                events = self._parse_json_events(json_data)
                if events:
                    logger.info(f"AJP: got {len(events)} events from JSON API {api_url}")
                    return events

        # 2) HTML fallback — works for server-rendered pages, fails silently for JS-only pages
        for html_url in HTML_CANDIDATES:
            html = await self.http.get_html(html_url)
            if not html:
                continue
            events = self._parse_html_events(html)
            if events:
                logger.info(f"AJP: got {len(events)} events from HTML {html_url}")
                return events
            log_empty_parse("ajp", html_url, html)

        logger.warning(
            "AJP: no events found via API or HTML. The site renders via client-side JS — "
            "consider a Playwright-based fetcher if this persists."
        )
        return events

    def _parse_json_events(self, data) -> list[ImportedEvent]:
        events: list[ImportedEvent] = []
        items = data if isinstance(data, list) else data.get("events") or data.get("data") or data.get("results") or []
        if not isinstance(items, list):
            return events

        for item in items:
            if not isinstance(item, dict):
                continue
            try:
                name = item.get("name") or item.get("title") or ""
                if not name:
                    continue
                event_date = parse_date(item.get("date") or item.get("start_date") or "") or date.today()
                source_id = str(item.get("id") or item.get("event_id") or "")
                slug_or_id = item.get("slug") or source_id
                source_url = f"{BASE_URL}/en/event/{slug_or_id}" if slug_or_id else None
                events.append(ImportedEvent(
                    name=name,
                    event_date=event_date,
                    organizer="AJP",
                    tier=self._map_tier(item.get("category", "")),
                    city=item.get("city"),
                    country=item.get("country"),
                    is_gi=item.get("gi", True),
                    is_nogi=item.get("nogi", False),
                    source="ajp",
                    source_id=source_id,
                    source_url=source_url,
                ))
            except Exception as e:
                logger.error(f"AJP: error parsing JSON event {item}: {e}")
        return events

    def _parse_html_events(self, html: str) -> list[ImportedEvent]:
        soup = BeautifulSoup(html, "lxml")
        events: list[ImportedEvent] = []
        seen: set[str] = set()

        # AJP wraps each event in an anchor pointing to /en/event/{id}
        for link in soup.find_all("a", href=True):
            href: str = link["href"]
            match = EVENT_LINK_RE.search(href)
            if not match:
                continue
            event_id = match.group(1)
            if event_id in seen:
                continue
            seen.add(event_id)

            name = text_of(select_first(link, "h3", "h4", ".event-title", ".title"), link.get_text(strip=True))
            if not name or len(name) > 250:
                continue

            location_text = text_of(select_first(link, ".location", ".venue", "p"))
            date_text = text_of(select_first(link, "time", ".date", ".event-date"))
            event_date = parse_date(date_text) or date.today()

            city, country = None, None
            if location_text:
                parts = [p.strip() for p in location_text.split(",")]
                if len(parts) >= 2:
                    city, country = parts[0], parts[-1]

            url = href if href.startswith("http") else f"{BASE_URL}{href}"
            events.append(ImportedEvent(
                name=name,
                event_date=event_date,
                organizer="AJP",
                tier="international",
                city=city,
                country=country,
                source="ajp",
                source_id=event_id,
                source_url=url,
            ))

        return events

    async def fetch_event_results(self, event_id: str) -> ImportedEvent | None:
        # Try JSON first
        for api_url in (
            f"{BASE_URL}/api/v1/events/{event_id}/results",
            f"{BASE_URL}/api/events/{event_id}/results",
        ):
            json_data = await self.http.get_json(api_url)
            if json_data:
                parsed = self._parse_json_results(event_id, json_data)
                if parsed and parsed.matches:
                    return parsed

        # HTML fallback
        url = f"{BASE_URL}/en/event/{event_id}/results"
        html = await self.http.get_html(url)
        if not html:
            html = await self.http.get_html(f"{BASE_URL}/en/event/{event_id}")
        if not html:
            return None

        return self._parse_html_results(event_id, html)

    def _parse_json_results(self, event_id: str, data: dict) -> ImportedEvent | None:
        try:
            event = ImportedEvent(
                name=data.get("event_name") or data.get("name") or f"AJP Event {event_id}",
                event_date=parse_date(data.get("date", "")) or date.today(),
                organizer="AJP",
                tier=self._map_tier(data.get("category", "")),
                source="ajp",
                source_id=event_id,
            )
            for match in data.get("results", data.get("matches", [])):
                if not isinstance(match, dict):
                    continue
                w_name = match.get("winner") or match.get("winner_name") or ""
                l_name = match.get("loser") or match.get("loser_name") or ""
                if isinstance(w_name, dict):
                    w_name = w_name.get("name", "")
                if isinstance(l_name, dict):
                    l_name = l_name.get("name", "")
                if not w_name or not l_name:
                    continue
                w_first, w_last = extract_name_parts(w_name)
                l_first, l_last = extract_name_parts(l_name)
                outcome, sub_type = parse_match_outcome(match.get("method", "points"))
                event.matches.append(ImportedMatch(
                    winner=ImportedAthlete(first_name=w_first, last_name=w_last, country=match.get("winner_country")),
                    loser=ImportedAthlete(first_name=l_first, last_name=l_last, country=match.get("loser_country")),
                    outcome=outcome,
                    submission_type=sub_type,
                    is_gi=match.get("gi", True),
                    round_name=match.get("round"),
                    division_name=match.get("division"),
                ))
            return event
        except Exception as e:
            logger.error(f"AJP: error parsing JSON results for event {event_id}: {e}")
            return None

    def _parse_html_results(self, event_id: str, html: str) -> ImportedEvent | None:
        soup = BeautifulSoup(html, "lxml")
        title = text_of(select_first(soup, "h1", ".event-title"), f"AJP Event {event_id}")
        event = ImportedEvent(
            name=title,
            event_date=date.today(),
            organizer="AJP",
            tier="international",
            source="ajp",
            source_id=event_id,
        )

        for row in select_any(soup, ".result-row", ".match-result", "tr.match", ".bracket-match"):
            names = row.select(".athlete-name, .competitor, .name, td.name")
            if len(names) < 2:
                continue
            winner_el = select_first(row, ".winner", ".highlighted", ".gold")
            result_el = select_first(row, ".method", ".result", ".outcome")
            name1, name2 = names[0].get_text(strip=True), names[1].get_text(strip=True)
            if winner_el and winner_el.get_text(strip=True) in name2:
                w_name, l_name = name2, name1
            else:
                w_name, l_name = name1, name2
            w_first, w_last = extract_name_parts(w_name)
            l_first, l_last = extract_name_parts(l_name)
            outcome, sub_type = parse_match_outcome(text_of(result_el, "points"))
            event.matches.append(ImportedMatch(
                winner=ImportedAthlete(first_name=w_first, last_name=w_last),
                loser=ImportedAthlete(first_name=l_first, last_name=l_last),
                outcome=outcome,
                submission_type=sub_type,
            ))

        if not event.matches:
            log_empty_parse("ajp", f"{BASE_URL}/en/event/{event_id}", html)
        logger.info(f"AJP event {event_id}: parsed {len(event.matches)} matches")
        return event

    @staticmethod
    def _map_tier(category: str) -> str:
        category = (category or "").lower()
        if "grand slam" in category or "world" in category:
            return "elite"
        if "continental" in category or "national" in category:
            return "national"
        if "international" in category:
            return "international"
        return "regional"
