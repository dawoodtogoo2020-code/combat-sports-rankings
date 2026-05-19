"""
Shared parsing utilities for all scrapers.
"""

import logging
import re
from datetime import date, datetime

from bs4 import BeautifulSoup, Tag

from app.ingestion.base import ImportedAthlete, ImportedMatch

logger = logging.getLogger(__name__)

# Country name -> ISO 3166-1 alpha-2 code
COUNTRY_MAP = {
    "united states": "US", "usa": "US", "us": "US", "u.s.a.": "US",
    "brazil": "BR", "brasil": "BR",
    "japan": "JP",
    "australia": "AU",
    "united kingdom": "GB", "uk": "GB", "england": "GB",
    "canada": "CA",
    "sweden": "SE",
    "france": "FR",
    "germany": "DE",
    "south korea": "KR", "korea": "KR",
    "mexico": "MX",
    "argentina": "AR",
    "colombia": "CO",
    "peru": "PE",
    "chile": "CL",
    "portugal": "PT",
    "spain": "ES",
    "italy": "IT",
    "netherlands": "NL",
    "poland": "PL",
    "russia": "RU",
    "uae": "AE", "united arab emirates": "AE",
    "ireland": "IE",
    "norway": "NO",
    "denmark": "DK",
    "new zealand": "NZ",
    "philippines": "PH",
    "singapore": "SG",
    "thailand": "TH",
    "indonesia": "ID",
    "south africa": "ZA",
}


def extract_name_parts(full_name: str) -> tuple[str, str]:
    """Split a full name into (first_name, last_name). Handles common patterns."""
    full_name = full_name.strip()
    # Remove suffixes
    full_name = re.sub(r"\s+(Jr\.?|Sr\.?|III|II|IV)$", "", full_name, flags=re.IGNORECASE)

    parts = full_name.split()
    if len(parts) == 0:
        return ("Unknown", "Unknown")
    if len(parts) == 1:
        return (parts[0], "")
    return (parts[0], " ".join(parts[1:]))


def parse_match_outcome(text: str) -> tuple[str, str | None]:
    """Parse outcome text into (outcome_type, submission_type).
    Examples: 'Sub (RNC)' -> ('submission', 'RNC'), 'Points 6-2' -> ('points', None)
    """
    text = text.strip().lower()

    # Submission with type
    sub_match = re.match(r"sub(?:mission)?\s*[\(\-:]\s*(.+?)[\)\s]*$", text, re.IGNORECASE)
    if sub_match:
        return ("submission", sub_match.group(1).strip().title())

    if "sub" in text or "tap" in text:
        return ("submission", None)
    if "pts" in text or "points" in text or "score" in text:
        return ("points", None)
    if "dec" in text or "decision" in text or "ref" in text:
        return ("decision", None)
    if "adv" in text or "advantage" in text:
        return ("advantage", None)
    if "dq" in text or "disq" in text:
        return ("dq", None)
    if "wo" in text or "walkover" in text or "bye" in text:
        return ("walkover", None)
    if "draw" in text or "tie" in text:
        return ("draw", None)

    return ("points", None)


def parse_scores(text: str) -> tuple[int | None, int | None]:
    """Extract winner/loser scores from text like '6-2', '4x2', '10 to 0'."""
    match = re.search(r"(\d+)\s*[-xX:to]+\s*(\d+)", text)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return (None, None)


def parse_division(text: str) -> dict:
    """Parse division text into components.
    Example: 'Adult / Male / Black / -76kg Gi' -> {belt, weight, is_gi, gender}
    """
    text = text.strip().lower()
    result = {"belt": None, "weight_class": None, "is_gi": True, "gender": "male"}

    # Gender
    if "female" in text or "women" in text:
        result["gender"] = "female"

    # Gi/No-Gi
    if "no-gi" in text or "nogi" in text or "no gi" in text:
        result["is_gi"] = False

    # Belt
    for belt in ["white", "blue", "purple", "brown", "black"]:
        if belt in text:
            result["belt"] = belt
            break

    # Weight class
    weight_match = re.search(r"[-+]?\d+\.?\d*\s*kg", text)
    if weight_match:
        result["weight_class"] = weight_match.group(0).strip()

    return result


def normalize_country(text: str | None) -> str | None:
    """Convert country name/code to ISO 3166-1 alpha-2."""
    if not text:
        return None
    text = text.strip().lower()
    # Already a 2-letter code
    if len(text) == 2:
        return text.upper()
    return COUNTRY_MAP.get(text)


def parse_date(text: str) -> date | None:
    """Parse various date formats into a date object."""
    if not text:
        return None
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
        "%b %d %Y",
        "%d-%b-%Y",
    ]
    text = text.strip()
    # Try ISO datetime first
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except (ValueError, AttributeError):
        pass
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    # Try year extraction as a last resort
    year_match = re.search(r"(19|20)\d{2}", text)
    if year_match:
        try:
            return date(int(year_match.group(0)), 1, 1)
        except ValueError:
            pass
    return None


def select_first(node: Tag, *selectors: str) -> Tag | None:
    """Try multiple CSS selectors, return first match. Safer than single-selector calls."""
    for sel in selectors:
        try:
            found = node.select_one(sel)
            if found:
                return found
        except Exception:
            continue
    return None


def select_any(node: Tag, *selectors: str) -> list[Tag]:
    """Try multiple selectors, return matches from the first one that yields anything."""
    for sel in selectors:
        try:
            found = node.select(sel)
            if found:
                return found
        except Exception:
            continue
    return []


def text_of(node: Tag | None, default: str = "") -> str:
    """Safe text extraction with default."""
    if not node:
        return default
    return node.get_text(strip=True)


def log_empty_parse(source: str, url: str, html_snippet: str | None = None) -> None:
    """Log when a parser returned nothing — useful for spotting selector drift in production."""
    msg = f"[{source}] No data parsed from {url}"
    if html_snippet:
        msg += f" — HTML head: {html_snippet[:200]!r}"
    logger.warning(msg)


def build_pseudo_matches_from_placements(
    placements: list[ImportedAthlete],
    division_name: str | None = None,
    is_gi: bool = True,
) -> list[ImportedMatch]:
    """Synthesize matches from a placement list (gold/silver/bronze).

    Federations like IBJJF and ADCC only publish final placements, not bracket-by-bracket
    match results. We treat the podium as a transitive ordering: 1st beat 2nd, 1st beat 3rd,
    2nd beat 3rd (and beat lower placers if present). This loses individual match outcomes
    but preserves the relative ranking signal the ELO engine needs.

    Caller should mark `outcome="points"` since method-of-victory is unknown.
    """
    matches: list[ImportedMatch] = []
    if len(placements) < 2:
        return matches

    # Each higher placer "beat" each lower placer
    for i, winner in enumerate(placements):
        for loser in placements[i + 1:]:
            matches.append(ImportedMatch(
                winner=winner,
                loser=loser,
                outcome="points",
                is_gi=is_gi,
                division_name=division_name,
            ))
    return matches


def parse_placement_list(
    soup: BeautifulSoup,
    division_selector: str = "h3, h4",
    item_selector: str = "li, tr, .placement-row",
) -> list[tuple[str, list[ImportedAthlete]]]:
    """Generic placement parser: returns [(division_name, [athletes_in_rank_order]), ...]

    Walks heading-keyed sections and extracts placers in document order. Handles the
    common pattern used by ADCC and similar federations where each weight class is a
    heading followed by a list of placers.
    """
    sections: list[tuple[str, list[ImportedAthlete]]] = []
    headings = soup.select(division_selector)

    for heading in headings:
        division_name = heading.get_text(strip=True)
        if not division_name or len(division_name) > 200:
            continue

        # Walk forward until the next heading at same or higher level
        placers: list[ImportedAthlete] = []
        for sibling in heading.find_all_next():
            if sibling in headings and sibling is not heading:
                break
            if not isinstance(sibling, Tag):
                continue
            if sibling.name in {"li", "tr"} or (
                sibling.has_attr("class") and "placement-row" in sibling.get("class", [])
            ):
                # Extract a name from the row
                name_text = sibling.get_text(" ", strip=True)
                # Strip leading rank numbers and medal alt-text
                name_text = re.sub(r"^\s*(\d+(?:st|nd|rd|th)?[\.\)\s-]+)", "", name_text)
                name_text = re.sub(r"\b(gold|silver|bronze)\s*medal\b", "", name_text, flags=re.IGNORECASE).strip()
                if not name_text or len(name_text) > 120:
                    continue
                first, last = extract_name_parts(name_text)
                if first == "Unknown":
                    continue
                placers.append(ImportedAthlete(first_name=first, last_name=last))
                if len(placers) >= 8:  # cap — don't capture entire participant lists
                    break

        if placers:
            sections.append((division_name, placers))

    return sections
