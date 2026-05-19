"""
SmoothComp scraper — the registration/results platform used by hundreds of BJJ,
grappling, and judo federations worldwide. This is the highest-coverage source.

SmoothComp exposes a partial JSON API at /api/event/{id}/results for events whose
organizers opted in; for everything else we fall back to HTML scraping with
multiple selector fallbacks.
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

BASE_URL = "https://smoothcomp.com"
LISTING_CANDIDATES = [
    f"{BASE_URL}/en/events?status=past&discipline=bjj",
    f"{BASE_URL}/en/events?status=past",
    f"{BASE_URL}/en/events",
]
EVENT_LINK_RE = re.compile(r"/event/(\d+)", re.IGNORECASE)


class SmoothCompIngester(BaseIngester):
    source_name = "smoothcomp"

    def __init__(self, http_client: ScraperHttpClient):
        self.http = http_client

    async def fetch_events(self, **kwargs) -> list[ImportedEvent]:
        events: list[ImportedEvent] = []

        for listing_url in LISTING_CANDIDATES:
            html = await self.http.get_html(listing_url)
            if not html:
                continue
            events = self._parse_listing(html, listing_url)
            if events:
                return events
            log_empty_parse("smoothcomp", listing_url, html)

        return events

    def _parse_listing(self, html: str, source_url: str) -> list[ImportedEvent]:
        soup = BeautifulSoup(html, "lxml")
        events: list[ImportedEvent] = []
        seen: set[str] = set()

        # Strategy 1: rich event cards with explicit classes
        cards = select_any(
            soup,
            ".event-card",
            "[data-event-id]",
            ".event-list-item",
            "li.event",
            "article.event",
            ".card",
        )

        for card in cards:
            event = self._event_from_card(card)
            if event and event.source_id and event.source_id not in seen:
                seen.add(event.source_id)
                events.append(event)

        # Strategy 2: anchor-driven fallback when no cards matched
        if not events:
            for link in soup.find_all("a", href=True):
                href = link["href"]
                match = EVENT_LINK_RE.search(href)
                if not match:
                    continue
                event_id = match.group(1)
                if event_id in seen:
                    continue
                name = link.get_text(strip=True)
                if not name or len(name) < 4 or len(name) > 250:
                    continue
                seen.add(event_id)
                events.append(ImportedEvent(
                    name=name,
                    event_date=date.today(),
                    organizer="SmoothComp",
                    tier="regional",
                    source="smoothcomp",
                    source_id=event_id,
                    source_url=href if href.startswith("http") else f"{BASE_URL}{href}",
                ))

        logger.info(f"SmoothComp: {len(events)} events from {source_url}")
        return events

    def _event_from_card(self, card) -> ImportedEvent | None:
        link = select_first(card, "a[href*='/event/']")
        href = link["href"] if link else ""
        id_match = EVENT_LINK_RE.search(href)
        if not id_match:
            return None
        event_id = id_match.group(1)

        name = text_of(
            select_first(card, "h3", "h4", ".event-name", ".card-title", ".event-title"),
            text_of(link),
        )
        if not name:
            return None

        date_node = select_first(card, "time[datetime]", ".event-date", ".date", "time")
        event_date = date.today()
        if date_node:
            dt = date_node.get("datetime") or date_node.get_text(strip=True)
            parsed = parse_date(dt or "")
            if parsed:
                event_date = parsed

        location_text = text_of(select_first(card, ".event-location", ".location", ".venue", ".city"))
        city, country = None, None
        if location_text:
            parts = [p.strip() for p in location_text.split(",")]
            if len(parts) >= 2:
                city, country = parts[0], parts[-1]
            elif len(parts) == 1:
                country = parts[0]

        return ImportedEvent(
            name=name,
            event_date=event_date,
            organizer="SmoothComp",
            tier="regional",
            city=city,
            country=country,
            source="smoothcomp",
            source_id=event_id,
            source_url=href if href.startswith("http") else f"{BASE_URL}{href}",
        )

    async def fetch_event_results(self, event_id: str) -> ImportedEvent | None:
        # Try JSON API first
        for api_url in (
            f"{BASE_URL}/api/event/{event_id}/results",
            f"{BASE_URL}/api/events/{event_id}/results",
            f"{BASE_URL}/en/event/{event_id}/results.json",
        ):
            json_data = await self.http.get_json(api_url)
            if json_data:
                event = self._parse_json_results(event_id, json_data)
                if event and event.matches:
                    return event

        # HTML fallback
        url = f"{BASE_URL}/en/event/{event_id}/results"
        html = await self.http.get_html(url)
        if not html:
            html = await self.http.get_html(f"{BASE_URL}/en/event/{event_id}")
        if not html:
            logger.warning(f"SmoothComp event {event_id}: no results page available")
            return None

        return self._parse_html_results(event_id, html, url)

    def _parse_json_results(self, event_id: str, data: dict) -> ImportedEvent | None:
        try:
            event = ImportedEvent(
                name=data.get("name", f"SmoothComp Event {event_id}"),
                event_date=parse_date(data.get("date", "")) or date.today(),
                organizer="SmoothComp",
                source="smoothcomp",
                source_id=event_id,
            )
            for match_data in data.get("matches", data.get("results", [])):
                if not isinstance(match_data, dict):
                    continue
                w_obj = match_data.get("winner", {})
                l_obj = match_data.get("loser", {})
                w_name = w_obj.get("name", "") if isinstance(w_obj, dict) else str(w_obj)
                l_name = l_obj.get("name", "") if isinstance(l_obj, dict) else str(l_obj)
                if not w_name or not l_name:
                    continue
                w_first, w_last = extract_name_parts(w_name)
                l_first, l_last = extract_name_parts(l_name)
                outcome, sub_type = parse_match_outcome(match_data.get("result", "points"))
                event.matches.append(ImportedMatch(
                    winner=ImportedAthlete(first_name=w_first, last_name=w_last),
                    loser=ImportedAthlete(first_name=l_first, last_name=l_last),
                    outcome=outcome,
                    submission_type=sub_type,
                    is_gi=match_data.get("gi", True),
                    round_name=match_data.get("round"),
                ))
            return event
        except Exception as e:
            logger.error(f"SmoothComp: error parsing JSON for event {event_id}: {e}")
            return None

    def _parse_html_results(self, event_id: str, html: str, url: str) -> ImportedEvent | None:
        soup = BeautifulSoup(html, "lxml")
        event_name = text_of(select_first(soup, "h1", ".event-title", ".event-name"), f"SmoothComp Event {event_id}")

        date_node = select_first(soup, "time[datetime]", ".event-date")
        event_date = date.today()
        if date_node:
            parsed = parse_date(date_node.get("datetime") or date_node.get_text(strip=True))
            if parsed:
                event_date = parsed

        event = ImportedEvent(
            name=event_name,
            event_date=event_date,
            organizer="SmoothComp",
            source="smoothcomp",
            source_id=event_id,
            source_url=url,
        )

        match_rows = select_any(
            soup,
            ".match-result",
            ".bracket-match",
            "tr.match",
            ".match-row",
            "li.match",
        )

        for row in match_rows:
            try:
                athletes = row.select(".athlete-name, .competitor-name, .fighter-name, td.name, .athlete")
                if len(athletes) < 2:
                    continue
                winner_el = select_first(row, ".winner", ".match-winner", ".highlighted", ".is-winner")
                result_el = select_first(row, ".match-outcome", ".result", ".method", ".outcome")
                name1, name2 = athletes[0].get_text(strip=True), athletes[1].get_text(strip=True)
                if winner_el and winner_el.get_text(strip=True) in name2:
                    w_name, l_name = name2, name1
                else:
                    w_name, l_name = name1, name2

                w_first, w_last = extract_name_parts(w_name)
                l_first, l_last = extract_name_parts(l_name)
                outcome, sub_type = parse_match_outcome(text_of(result_el, "points"))
                div_info = parse_division(text_of(select_first(row, ".division", ".category"))) if select_first(row, ".division", ".category") else {}

                event.matches.append(ImportedMatch(
                    winner=ImportedAthlete(first_name=w_first, last_name=w_last),
                    loser=ImportedAthlete(first_name=l_first, last_name=l_last),
                    outcome=outcome,
                    submission_type=sub_type,
                    is_gi=div_info.get("is_gi", True),
                ))
            except Exception as e:
                logger.error(f"SmoothComp: error parsing match row: {e}")

        if not event.matches:
            log_empty_parse("smoothcomp", url, html)
        logger.info(f"SmoothComp event {event_id}: parsed {len(event.matches)} matches")
        return event
