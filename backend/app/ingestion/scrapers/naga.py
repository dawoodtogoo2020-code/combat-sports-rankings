"""
NAGA scraper — North American Grappling Association results.
NAGA may provide CSV downloads; falls back to HTML scraping.
"""

import logging
import re
from datetime import date

from bs4 import BeautifulSoup

from app.ingestion.base import BaseIngester, ImportedEvent, ImportedMatch, ImportedAthlete
from app.ingestion.http_client import ScraperHttpClient
from app.ingestion.scrapers.parsers import (
    extract_name_parts, parse_match_outcome, parse_date,
)

logger = logging.getLogger(__name__)

BASE_URL = "https://www.nagafighter.com"


class NagaIngester(BaseIngester):
    source_name = "naga"

    def __init__(self, http_client: ScraperHttpClient):
        self.http = http_client

    async def fetch_events(self, **kwargs) -> list[ImportedEvent]:
        """Fetch past NAGA events."""
        events = []

        html = await self.http.get_html(f"{BASE_URL}/past-events")
        if not html:
            html = await self.http.get_html(f"{BASE_URL}/results")
        if not html:
            logger.warning("Could not fetch NAGA events page")
            return events

        soup = BeautifulSoup(html, "lxml")
        for card in soup.select(".event-item, .event, article, .result-item"):
            try:
                name_el = card.select_one("h2, h3, .title, a")
                link_el = card.select_one("a[href]")
                date_el = card.select_one(".date, time, .event-date")

                if not name_el:
                    continue

                name = name_el.get_text(strip=True)
                href = link_el.get("href", "") if link_el else ""

                event_date = date.today()
                if date_el:
                    parsed = parse_date(date_el.get_text(strip=True))
                    if parsed:
                        event_date = parsed

                # Extract city from event name (NAGA events often named "NAGA Chicago")
                city = None
                city_match = re.search(r"NAGA\s+(.+?)(?:\s+\d{4})?$", name, re.IGNORECASE)
                if city_match:
                    city = city_match.group(1).strip()

                source_id = re.search(r"/(\d+)", href)

                events.append(ImportedEvent(
                    name=name,
                    event_date=event_date,
                    organizer="NAGA",
                    tier="regional",
                    city=city,
                    country="US",
                    is_gi=True,
                    is_nogi=True,
                    source="naga",
                    source_id=source_id.group(1) if source_id else "",
                    source_url=f"{BASE_URL}{href}" if href.startswith("/") else href,
                ))
            except Exception as e:
                logger.error(f"Error parsing NAGA event: {e}")

        logger.info(f"Found {len(events)} NAGA events")
        return events

    async def fetch_event_results(self, event_id: str) -> ImportedEvent | None:
        """Fetch results for a NAGA event."""
        # Check for CSV download first
        csv_resp = await self.http.get(f"{BASE_URL}/results/{event_id}/download")
        if csv_resp and csv_resp.status_code == 200 and "text/csv" in csv_resp.headers.get("content-type", ""):
            return self._parse_csv_results(event_id, csv_resp.text)

        # HTML fallback
        html = await self.http.get_html(f"{BASE_URL}/results/{event_id}")
        if not html:
            return None

        return self._parse_html_results(event_id, html)

    def _parse_csv_results(self, event_id: str, csv_text: str) -> ImportedEvent | None:
        """Delegate to CSV ingester if NAGA provides CSV downloads."""
        from app.ingestion.csv_ingester import CsvIngester
        try:
            ingester = CsvIngester()
            events = ingester.parse_csv_text(csv_text) if hasattr(ingester, "parse_csv_text") else []
            return events[0] if events else None
        except Exception as e:
            logger.error(f"Error parsing NAGA CSV: {e}")
            return None

    def _parse_html_results(self, event_id: str, html: str) -> ImportedEvent | None:
        soup = BeautifulSoup(html, "lxml")

        title_el = soup.select_one("h1, .event-title")
        event_name = title_el.get_text(strip=True) if title_el else f"NAGA Event {event_id}"

        event = ImportedEvent(
            name=event_name,
            event_date=date.today(),
            organizer="NAGA",
            tier="regional",
            is_gi=True,
            is_nogi=True,
            source="naga",
            source_id=event_id,
        )

        for row in soup.select(".match-result, .result-row, tr.match, .bracket-match"):
            try:
                names = row.select(".name, .athlete, .competitor, td")
                if len(names) < 2:
                    continue

                winner_el = row.select_one(".winner, .gold, .first-place")
                result_el = row.select_one(".method, .result, .outcome")

                name1 = names[0].get_text(strip=True)
                name2 = names[1].get_text(strip=True)
                if not name1 or not name2:
                    continue

                if winner_el:
                    wt = winner_el.get_text(strip=True)
                    w_name, l_name = (name1, name2) if wt in name1 else (name2, name1)
                else:
                    w_name, l_name = name1, name2

                w_first, w_last = extract_name_parts(w_name)
                l_first, l_last = extract_name_parts(l_name)

                outcome, sub_type = "points", None
                if result_el:
                    outcome, sub_type = parse_match_outcome(result_el.get_text(strip=True))

                event.matches.append(ImportedMatch(
                    winner=ImportedAthlete(first_name=w_first, last_name=w_last),
                    loser=ImportedAthlete(first_name=l_first, last_name=l_last),
                    outcome=outcome,
                    submission_type=sub_type,
                ))
            except Exception as e:
                logger.error(f"Error parsing NAGA match: {e}")

        logger.info(f"Parsed {len(event.matches)} matches from NAGA event {event_id}")
        return event
