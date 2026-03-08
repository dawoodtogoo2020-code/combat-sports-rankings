"""
Fuzzy athlete duplicate detection using Levenshtein distance.

Scores candidate pairs by: name similarity + shared gym + country + belt + weight class + event overlap.
Returns pairs with confidence scores for admin review.
"""

from dataclasses import dataclass


@dataclass
class DuplicateCandidate:
    athlete_a_id: str
    athlete_a_name: str
    athlete_b_id: str
    athlete_b_name: str
    confidence: float  # 0.0 – 1.0
    reasons: list[str]


def _levenshtein(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)

    if len(s2) == 0:
        return len(s1)

    prev_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row

    return prev_row[-1]


def name_similarity(name_a: str, name_b: str) -> float:
    """Return 0.0-1.0 similarity score based on normalized Levenshtein distance."""
    a = name_a.lower().strip()
    b = name_b.lower().strip()

    if a == b:
        return 1.0

    max_len = max(len(a), len(b))
    if max_len == 0:
        return 1.0

    distance = _levenshtein(a, b)
    return max(0.0, 1.0 - distance / max_len)


def score_duplicate_pair(
    athlete_a: dict,
    athlete_b: dict,
    shared_events: int = 0,
) -> DuplicateCandidate:
    """
    Score a potential duplicate pair.

    athlete dict keys: id, display_name, gym_id, country, country_code,
                       belt_rank_id, weight_class_id
    """
    score = 0.0
    reasons = []

    # Name similarity (0 – 0.5 weight)
    ns = name_similarity(athlete_a["display_name"], athlete_b["display_name"])
    if ns >= 0.85:
        score += ns * 0.5
        reasons.append(f"Name similarity: {ns:.0%}")
    elif ns >= 0.7:
        score += ns * 0.35
        reasons.append(f"Name similarity: {ns:.0%}")
    else:
        # Names too different — unlikely duplicate
        return DuplicateCandidate(
            athlete_a_id=str(athlete_a["id"]),
            athlete_a_name=athlete_a["display_name"],
            athlete_b_id=str(athlete_b["id"]),
            athlete_b_name=athlete_b["display_name"],
            confidence=0.0,
            reasons=[],
        )

    # Same gym
    if athlete_a.get("gym_id") and athlete_a["gym_id"] == athlete_b.get("gym_id"):
        score += 0.15
        reasons.append("Same gym")

    # Same country
    if athlete_a.get("country_code") and athlete_a["country_code"] == athlete_b.get("country_code"):
        score += 0.1
        reasons.append("Same country")

    # Same belt rank
    if athlete_a.get("belt_rank_id") and athlete_a["belt_rank_id"] == athlete_b.get("belt_rank_id"):
        score += 0.1
        reasons.append("Same belt rank")

    # Same weight class
    if athlete_a.get("weight_class_id") and athlete_a["weight_class_id"] == athlete_b.get("weight_class_id"):
        score += 0.1
        reasons.append("Same weight class")

    # Event overlap
    if shared_events > 0:
        event_score = min(shared_events * 0.05, 0.15)
        score += event_score
        reasons.append(f"Shared {shared_events} event(s)")

    return DuplicateCandidate(
        athlete_a_id=str(athlete_a["id"]),
        athlete_a_name=athlete_a["display_name"],
        athlete_b_id=str(athlete_b["id"]),
        athlete_b_name=athlete_b["display_name"],
        confidence=min(score, 1.0),
        reasons=reasons,
    )
