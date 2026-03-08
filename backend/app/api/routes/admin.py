import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File, status
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User, UserRole
from app.models.athlete import Athlete
from app.models.gym import Gym
from app.models.event import Event, EventTier
from app.models.match import Match, MatchOutcome, VerificationStatus
from app.models.social import Post
from app.models.rating import RatingHistory
from app.models.audit_log import AuditLog, AuditAction
from app.models.data_source import DataSource
from app.middleware.auth import require_admin
from app.elo.engine import EloEngine, PlayerInfo, MatchContext, CompetitionTier, MatchOutcome as EloMatchOutcome
from app.ingestion.csv_ingester import CsvIngester
from pydantic import BaseModel, Field

router = APIRouter()
elo_engine = EloEngine()


class DashboardStats(BaseModel):
    total_athletes: int
    total_gyms: int
    total_events: int
    total_matches: int
    total_users: int
    total_posts: int


class EloAdjustment(BaseModel):
    athlete_id: uuid.UUID
    new_rating: float = Field(ge=100, le=3000)
    reason: str = Field(min_length=1, max_length=500)


class MergeAthletes(BaseModel):
    primary_id: uuid.UUID
    duplicate_id: uuid.UUID


# ─── Helpers ───

def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def _log_action(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    action: AuditAction,
    target_type: str,
    target_id: str,
    details: dict | None = None,
    ip_address: str | None = None,
):
    entry = AuditLog(
        user_id=user_id,
        action=action.value,
        target_type=target_type,
        target_id=target_id,
        details=details,
        ip_address=ip_address,
    )
    db.add(entry)


# ─── Dashboard ───

@router.get("/dashboard", response_model=DashboardStats)
async def admin_dashboard(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    athletes = await db.execute(select(func.count()).select_from(Athlete))
    gyms = await db.execute(select(func.count()).select_from(Gym))
    events = await db.execute(select(func.count()).select_from(Event))
    matches = await db.execute(select(func.count()).select_from(Match))
    users = await db.execute(select(func.count()).select_from(User))
    posts = await db.execute(select(func.count()).select_from(Post))

    return DashboardStats(
        total_athletes=athletes.scalar(),
        total_gyms=gyms.scalar(),
        total_events=events.scalar(),
        total_matches=matches.scalar(),
        total_users=users.scalar(),
        total_posts=posts.scalar(),
    )


# ─── Athletes ───

@router.post("/athletes/{athlete_id}/adjust-elo")
async def adjust_elo(
    athlete_id: uuid.UUID,
    data: EloAdjustment,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(Athlete).where(Athlete.id == athlete_id))
    athlete = result.scalar_one_or_none()
    if not athlete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found")

    old_rating = athlete.elo_rating
    athlete.elo_rating = data.new_rating
    athlete.gi_rating = data.new_rating
    athlete.nogi_rating = data.new_rating
    athlete.peak_rating = max(athlete.peak_rating, data.new_rating)

    history = RatingHistory(
        athlete_id=athlete.id,
        rating_before=old_rating,
        rating_after=data.new_rating,
        rating_change=round(data.new_rating - old_rating, 1),
        rating_type="overall",
    )
    db.add(history)

    await _log_action(
        db, user_id=user.id, action=AuditAction.ELO_ADJUST,
        target_type="athlete", target_id=str(athlete_id),
        details={"old_rating": old_rating, "new_rating": data.new_rating, "reason": data.reason},
        ip_address=_client_ip(request),
    )

    return {"message": f"Rating adjusted from {old_rating} to {data.new_rating}", "reason": data.reason}


@router.delete("/athletes/{athlete_id}")
async def delete_athlete(
    athlete_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(Athlete).where(Athlete.id == athlete_id))
    athlete = result.scalar_one_or_none()
    if not athlete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found")

    athlete.is_active = False

    await _log_action(
        db, user_id=user.id, action=AuditAction.ATHLETE_DELETE,
        target_type="athlete", target_id=str(athlete_id),
        details={"display_name": athlete.display_name},
        ip_address=_client_ip(request),
    )

    return {"message": "Athlete deactivated"}


@router.post("/athletes/merge")
async def merge_athletes(
    data: MergeAthletes,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    primary = await db.execute(select(Athlete).where(Athlete.id == data.primary_id))
    primary_athlete = primary.scalar_one_or_none()
    if not primary_athlete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Primary athlete not found")

    duplicate = await db.execute(select(Athlete).where(Athlete.id == data.duplicate_id))
    dup_athlete = duplicate.scalar_one_or_none()
    if not dup_athlete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Duplicate athlete not found")

    await db.execute(
        update(Match).where(Match.winner_id == data.duplicate_id).values(winner_id=data.primary_id)
    )
    await db.execute(
        update(Match).where(Match.loser_id == data.duplicate_id).values(loser_id=data.primary_id)
    )
    await db.execute(
        update(RatingHistory).where(RatingHistory.athlete_id == data.duplicate_id).values(athlete_id=data.primary_id)
    )

    primary_athlete.total_matches += dup_athlete.total_matches
    primary_athlete.wins += dup_athlete.wins
    primary_athlete.losses += dup_athlete.losses
    primary_athlete.draws += dup_athlete.draws
    primary_athlete.submissions += dup_athlete.submissions

    dup_athlete.is_active = False

    await _log_action(
        db, user_id=user.id, action=AuditAction.ATHLETE_MERGE,
        target_type="athlete", target_id=str(data.primary_id),
        details={"merged_from": str(data.duplicate_id), "merged_name": dup_athlete.display_name},
        ip_address=_client_ip(request),
    )

    return {"message": f"Merged {dup_athlete.display_name} into {primary_athlete.display_name}"}


# ─── Match Verification ───

@router.patch("/matches/{match_id}/verify")
async def verify_match(
    match_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalar_one_or_none()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

    match.verification_status = VerificationStatus.SOURCE_VERIFIED
    match.is_verified = True

    await _log_action(
        db, user_id=user.id, action=AuditAction.MATCH_VERIFY,
        target_type="match", target_id=str(match_id),
        details={"new_status": "source_verified"},
        ip_address=_client_ip(request),
    )

    return {"message": "Match verified"}


@router.patch("/matches/{match_id}/reject")
async def reject_match(
    match_id: uuid.UUID,
    reason: str = Query(default="", max_length=500),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalar_one_or_none()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

    match.verification_status = VerificationStatus.REJECTED
    match.is_verified = False

    await _log_action(
        db, user_id=user.id, action=AuditAction.MATCH_REJECT,
        target_type="match", target_id=str(match_id),
        details={"reason": reason},
        ip_address=_client_ip(request) if request else "unknown",
    )

    return {"message": "Match rejected"}


# ─── Recalculate Rankings ───

@router.post("/recalculate-rankings")
async def recalculate_rankings(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    """Recalculate all ELO ratings from scratch based on verified match history."""
    await db.execute(
        update(Athlete).values(
            elo_rating=1200.0, gi_rating=1200.0, nogi_rating=1200.0,
            peak_rating=1200.0, wins=0, losses=0, draws=0, submissions=0, total_matches=0,
        )
    )

    # Only use verified matches for ranking calculation
    result = await db.execute(
        select(Match)
        .where(Match.verification_status.in_([
            VerificationStatus.SOURCE_VERIFIED,
            VerificationStatus.CROSS_CHECKED,
        ]))
        .order_by(Match.created_at.asc())
    )
    matches = result.scalars().all()

    processed = 0
    for match in matches:
        winner_result = await db.execute(select(Athlete).where(Athlete.id == match.winner_id))
        winner = winner_result.scalar_one_or_none()
        loser_result = await db.execute(select(Athlete).where(Athlete.id == match.loser_id))
        loser = loser_result.scalar_one_or_none()

        if not winner or not loser:
            continue

        winner_info = PlayerInfo(
            rating=winner.gi_rating if match.is_gi else winner.nogi_rating,
            total_matches=winner.total_matches,
            years_experience=winner.years_training or 0,
        )
        loser_info = PlayerInfo(
            rating=loser.gi_rating if match.is_gi else loser.nogi_rating,
            total_matches=loser.total_matches,
            years_experience=loser.years_training or 0,
        )

        event_result = await db.execute(select(Event).where(Event.id == match.event_id))
        event = event_result.scalar_one_or_none()
        tier = CompetitionTier(event.tier.value) if event else CompetitionTier.LOCAL

        try:
            outcome = EloMatchOutcome(match.outcome.value)
        except (ValueError, AttributeError):
            outcome = EloMatchOutcome.POINTS

        ctx = MatchContext(
            competition_tier=tier, outcome=outcome,
            is_gi=match.is_gi, round_name=match.round_name,
        )

        elo_result = elo_engine.calculate(winner_info, loser_info, ctx, is_draw=match.is_draw)

        if match.is_gi:
            winner.gi_rating = elo_result.winner_new_rating
            loser.gi_rating = elo_result.loser_new_rating
        else:
            winner.nogi_rating = elo_result.winner_new_rating
            loser.nogi_rating = elo_result.loser_new_rating

        winner.elo_rating = round((winner.gi_rating + winner.nogi_rating) / 2, 1)
        loser.elo_rating = round((loser.gi_rating + loser.nogi_rating) / 2, 1)
        winner.peak_rating = max(winner.peak_rating, winner.elo_rating)
        loser.peak_rating = max(loser.peak_rating, loser.elo_rating)

        if match.is_draw:
            winner.draws += 1
            loser.draws += 1
        else:
            winner.wins += 1
            loser.losses += 1
        winner.total_matches += 1
        loser.total_matches += 1

        if match.outcome and match.outcome.value == "submission":
            winner.submissions += 1

        match.winner_elo_before = winner_info.rating
        match.winner_elo_after = elo_result.winner_new_rating
        match.loser_elo_before = loser_info.rating
        match.loser_elo_after = elo_result.loser_new_rating
        match.elo_change = elo_result.winner_change
        match.k_factor_used = elo_result.k_factor_used
        match.elo_calculated = True

        processed += 1

    await _log_action(
        db, user_id=user.id, action=AuditAction.RECALCULATE,
        target_type="system", target_id="rankings",
        details={"matches_processed": processed},
        ip_address=_client_ip(request),
    )

    return {"message": f"Recalculated {processed} verified matches"}


# ─── Users ───

@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
):
    query = select(User).order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "username": u.username,
            "full_name": u.full_name,
            "role": u.role.value,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: uuid.UUID,
    role: str = Query(pattern=r"^(user|athlete|gym_owner|admin)$"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    old_role = target.role.value
    target.role = UserRole(role)

    await _log_action(
        db, user_id=user.id, action=AuditAction.ROLE_CHANGE,
        target_type="user", target_id=str(user_id),
        details={"old_role": old_role, "new_role": role},
        ip_address=_client_ip(request) if request else "unknown",
    )

    return {"message": f"Role updated to {role}"}


# ─── Gyms ───

@router.post("/gyms/{gym_id}/verify")
async def verify_gym(
    gym_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(Gym).where(Gym.id == gym_id))
    gym = result.scalar_one_or_none()
    if not gym:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gym not found")

    gym.is_verified = True

    await _log_action(
        db, user_id=user.id, action=AuditAction.GYM_VERIFY,
        target_type="gym", target_id=str(gym_id),
        details={"gym_name": gym.name},
        ip_address=_client_ip(request),
    )

    return {"message": f"Gym '{gym.name}' verified"}


# ─── Posts ───

@router.delete("/posts/{post_id}")
async def moderate_post(
    post_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    post.is_published = False

    await _log_action(
        db, user_id=user.id, action=AuditAction.POST_MODERATE,
        target_type="post", target_id=str(post_id),
        ip_address=_client_ip(request),
    )

    return {"message": "Post hidden"}


# ─── Audit Log ───

@router.get("/audit-log")
async def list_audit_logs(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
    action: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    query = select(AuditLog).order_by(AuditLog.created_at.desc())

    if action:
        query = query.where(AuditLog.action == action)

    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    logs = result.scalars().all()

    return {
        "entries": [
            {
                "id": str(log.id),
                "user_id": str(log.user_id),
                "user_name": log.user.full_name or log.user.username if log.user else "Unknown",
                "action": log.action,
                "target_type": log.target_type,
                "target_id": log.target_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ],
        "total_count": total,
        "page": page,
        "page_size": page_size,
    }


# ─── Data Sources ───

@router.get("/data-sources")
async def list_data_sources(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(DataSource).order_by(DataSource.name))
    sources = result.scalars().all()
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "slug": s.slug,
            "base_url": s.base_url,
            "description": s.description,
            "ingestion_method": s.ingestion_method,
            "robots_txt_status": s.robots_txt_status,
            "tos_reviewed": s.tos_reviewed,
            "tos_allows_scraping": s.tos_allows_scraping,
            "compliance_notes": s.compliance_notes,
            "is_active": s.is_active,
            "last_sync_at": s.last_sync_at.isoformat() if s.last_sync_at else None,
            "created_at": s.created_at.isoformat(),
        }
        for s in sources
    ]


@router.patch("/data-sources/{source_id}")
async def update_data_source(
    source_id: uuid.UUID,
    is_active: bool | None = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(DataSource).where(DataSource.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data source not found")

    if is_active is not None:
        source.is_active = is_active

    return {"message": f"Data source '{source.name}' updated"}


# ─── Duplicate Detection ───

@router.get("/athletes/duplicates")
async def detect_duplicates(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
    min_confidence: float = Query(0.6, ge=0.0, le=1.0),
    limit: int = Query(50, ge=1, le=200),
):
    """Find potential duplicate athletes using fuzzy name matching."""
    from app.services.duplicate_detection import score_duplicate_pair

    result = await db.execute(
        select(Athlete).where(Athlete.is_active == True).order_by(Athlete.display_name)
    )
    athletes = result.scalars().all()

    candidates = []
    athlete_dicts = [
        {
            "id": a.id,
            "display_name": a.display_name,
            "gym_id": a.gym_id,
            "country_code": a.country_code,
            "belt_rank_id": a.belt_rank_id,
            "weight_class_id": a.weight_class_id,
        }
        for a in athletes
    ]

    for i in range(len(athlete_dicts)):
        for j in range(i + 1, len(athlete_dicts)):
            pair = score_duplicate_pair(athlete_dicts[i], athlete_dicts[j])
            if pair.confidence >= min_confidence:
                candidates.append(pair)

    candidates.sort(key=lambda c: c.confidence, reverse=True)
    candidates = candidates[:limit]

    return [
        {
            "athlete_a_id": c.athlete_a_id,
            "athlete_a_name": c.athlete_a_name,
            "athlete_b_id": c.athlete_b_id,
            "athlete_b_name": c.athlete_b_name,
            "confidence": round(c.confidence, 3),
            "reasons": c.reasons,
        }
        for c in candidates
    ]


# ─── CSV Import ───

TIER_MAP = {
    "local": EventTier.LOCAL,
    "regional": EventTier.REGIONAL,
    "national": EventTier.NATIONAL,
    "international": EventTier.INTERNATIONAL,
    "elite": EventTier.ELITE,
}

ELO_TIER_MAP = {
    EventTier.LOCAL: CompetitionTier.LOCAL,
    EventTier.REGIONAL: CompetitionTier.REGIONAL,
    EventTier.NATIONAL: CompetitionTier.NATIONAL,
    EventTier.INTERNATIONAL: CompetitionTier.INTERNATIONAL,
    EventTier.ELITE: CompetitionTier.ELITE,
}


@router.post("/import-csv")
async def import_csv(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    """Import match data from a CSV file, create events/athletes as needed, and calculate ELO."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are accepted")

    contents = await file.read()
    csv_text = contents.decode("utf-8-sig")

    ingester = CsvIngester()
    try:
        imported_events = ingester.parse_csv(csv_text)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"CSV parse error: {str(e)}")

    if not imported_events:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No events found in CSV")

    events_created = 0
    matches_created = 0
    athletes_created = 0

    # Get default sport (BJJ)
    from app.models.sport import Sport
    sport_result = await db.execute(select(Sport).where(Sport.slug == "bjj"))
    default_sport = sport_result.scalar_one_or_none()

    for imp_event in imported_events:
        # Find or create event
        slug = imp_event.name.lower().replace(" ", "-").replace("/", "-")[:250]
        event_result = await db.execute(select(Event).where(Event.slug == slug))
        event = event_result.scalar_one_or_none()

        if not event:
            tier = TIER_MAP.get(imp_event.tier.lower(), EventTier.LOCAL)
            event = Event(
                name=imp_event.name,
                slug=slug,
                event_date=imp_event.event_date,
                end_date=imp_event.end_date,
                organizer=imp_event.organizer,
                tier=tier,
                city=imp_event.city,
                country=imp_event.country,
                is_gi=imp_event.is_gi,
                is_nogi=imp_event.is_nogi,
                source=imp_event.source,
                source_id=imp_event.source_id,
                source_url=imp_event.source_url,
                is_published=True,
                matches_imported=True,
            )
            db.add(event)
            await db.flush()
            events_created += 1

        for imp_match in imp_event.matches:
            # Find or create winner
            winner = await _find_or_create_athlete(
                db, imp_match.winner, default_sport.id if default_sport else None
            )
            if winner._created:
                athletes_created += 1

            # Find or create loser
            loser = await _find_or_create_athlete(
                db, imp_match.loser, default_sport.id if default_sport else None
            )
            if loser._created:
                athletes_created += 1

            # Calculate ELO
            winner_info = PlayerInfo(
                rating=winner.elo_rating,
                total_matches=winner.total_matches,
                years_experience=winner.years_training or 0,
            )
            loser_info = PlayerInfo(
                rating=loser.elo_rating,
                total_matches=loser.total_matches,
                years_experience=loser.years_training or 0,
            )

            elo_tier = ELO_TIER_MAP.get(event.tier, CompetitionTier.LOCAL)
            try:
                outcome = EloMatchOutcome(imp_match.outcome)
            except ValueError:
                outcome = EloMatchOutcome.POINTS

            ctx = MatchContext(
                competition_tier=elo_tier,
                outcome=outcome,
                is_gi=imp_match.is_gi,
                round_name=imp_match.round_name,
            )

            elo_result = elo_engine.calculate(winner_info, loser_info, ctx, is_draw=imp_match.is_draw)

            # Create match record
            try:
                match_outcome = MatchOutcome(imp_match.outcome)
            except ValueError:
                match_outcome = MatchOutcome.POINTS

            match = Match(
                event_id=event.id,
                winner_id=winner.id,
                loser_id=loser.id,
                outcome=match_outcome,
                is_draw=imp_match.is_draw,
                submission_type=imp_match.submission_type,
                winner_score=imp_match.winner_score,
                loser_score=imp_match.loser_score,
                is_gi=imp_match.is_gi,
                round_name=imp_match.round_name,
                match_date=imp_match.match_date or datetime.combine(event.event_date, datetime.min.time()),
                winner_elo_before=winner.elo_rating,
                winner_elo_after=elo_result.winner_new_rating,
                loser_elo_before=loser.elo_rating,
                loser_elo_after=elo_result.loser_new_rating,
                elo_change=elo_result.winner_change,
                k_factor_used=elo_result.k_factor_used,
                elo_calculated=True,
                is_verified=False,
                verification_status=VerificationStatus.PENDING,
                source=imp_event.source or "csv",
                source_id=imp_match.source_id,
            )
            db.add(match)
            await db.flush()

            # Update athlete ratings and stats
            old_w = winner.elo_rating
            old_l = loser.elo_rating
            winner.elo_rating = elo_result.winner_new_rating
            loser.elo_rating = elo_result.loser_new_rating

            if imp_match.is_gi:
                winner.gi_rating = winner.gi_rating + elo_result.winner_change
                loser.gi_rating = loser.gi_rating + elo_result.loser_change
            else:
                winner.nogi_rating = winner.nogi_rating + elo_result.winner_change
                loser.nogi_rating = loser.nogi_rating + elo_result.loser_change

            winner.peak_rating = max(winner.peak_rating, winner.elo_rating)
            loser.peak_rating = max(loser.peak_rating, loser.elo_rating)

            winner.total_matches += 1
            winner.wins += 1
            loser.total_matches += 1
            loser.losses += 1
            if imp_match.outcome == "submission":
                winner.submissions += 1

            # Rating history
            match_ts = imp_match.match_date or datetime.combine(event.event_date, datetime.min.time())
            db.add(RatingHistory(
                athlete_id=winner.id, match_id=match.id,
                rating_before=old_w, rating_after=elo_result.winner_new_rating,
                rating_change=elo_result.winner_change, rating_type="overall",
                recorded_at=match_ts,
            ))
            db.add(RatingHistory(
                athlete_id=loser.id, match_id=match.id,
                rating_before=old_l, rating_after=elo_result.loser_new_rating,
                rating_change=elo_result.loser_change, rating_type="overall",
                recorded_at=match_ts,
            ))
            matches_created += 1

    await _log_action(
        db, user_id=user.id, action=AuditAction.IMPORT_DATA,
        target_type="system", target_id="csv_import",
        details={
            "filename": file.filename,
            "events_imported": events_created,
            "matches_imported": matches_created,
            "athletes_created": athletes_created,
        },
        ip_address=_client_ip(request),
    )

    return {
        "message": "CSV import complete",
        "events_imported": events_created,
        "matches_imported": matches_created,
        "athletes_created": athletes_created,
    }


async def _find_or_create_athlete(db: AsyncSession, imp_athlete, sport_id=None):
    """Find an existing athlete by name or create a new one."""
    display_name = f"{imp_athlete.first_name} {imp_athlete.last_name}"

    result = await db.execute(
        select(Athlete).where(
            Athlete.display_name == display_name,
            Athlete.is_active == True,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing._created = False
        return existing

    athlete = Athlete(
        first_name=imp_athlete.first_name,
        last_name=imp_athlete.last_name,
        display_name=display_name,
        gender=imp_athlete.gender or "male",
        country=imp_athlete.country,
        sport_id=sport_id,
        elo_rating=1200.0,
        gi_rating=1200.0,
        nogi_rating=1200.0,
        peak_rating=1200.0,
        total_matches=0,
        wins=0,
        losses=0,
        draws=0,
        submissions=0,
        is_active=True,
        is_verified=False,
    )
    db.add(athlete)
    await db.flush()
    athlete._created = True
    return athlete
