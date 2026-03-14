"""
Shared parsing utilities for all scrapers.
"""

import re
from datetime import date, datetime

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
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
    ]
    text = text.strip()
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None
