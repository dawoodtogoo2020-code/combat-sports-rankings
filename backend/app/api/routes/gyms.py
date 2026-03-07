import uuid
import re
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.gym import Gym
from app.models.athlete import Athlete
from app.schemas.gym import GymCreate, GymRead, GymUpdate
from app.schemas.athlete import AthleteListItem
from app.middleware.auth import get_current_user, require_admin, require_gym_owner
from app.models.user import User
from app.middleware.rate_limit import limiter

router = APIRouter()


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-+", "-", text)


@router.get("/", response_model=list[GymRead])
@limiter.limit("30/minute")
async def list_gyms(
    request,
    db: AsyncSession = Depends(get_db),
    search: str | None = Query(None, max_length=200),
    country: str | None = Query(None, max_length=100),
    city: str | None = Query(None, max_length=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
):
    query = select(Gym).where(Gym.is_active == True)

    if search:
        query = query.where(Gym.name.ilike(f"%{search}%"))
    if country:
        query = query.where(Gym.country == country)
    if city:
        query = query.where(Gym.city == city)

    query = query.order_by(Gym.member_count.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{gym_id}", response_model=GymRead)
@limiter.limit("60/minute")
async def get_gym(request, gym_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Gym).where(Gym.id == gym_id))
    gym = result.scalar_one_or_none()
    if not gym:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gym not found")
    return gym


@router.post("/", response_model=GymRead, status_code=status.HTTP_201_CREATED)
async def create_gym(
    data: GymCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    slug = slugify(data.name)
    # Ensure unique slug
    existing = await db.execute(select(Gym).where(Gym.slug == slug))
    if existing.scalar_one_or_none():
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"

    gym = Gym(**data.model_dump(exclude_unset=True), slug=slug, owner_id=user.id)
    db.add(gym)
    await db.flush()
    await db.refresh(gym)
    return gym


@router.patch("/{gym_id}", response_model=GymRead)
async def update_gym(
    gym_id: uuid.UUID,
    data: GymUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_gym_owner),
):
    result = await db.execute(select(Gym).where(Gym.id == gym_id))
    gym = result.scalar_one_or_none()
    if not gym:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gym not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(gym, field, value)

    await db.flush()
    await db.refresh(gym)
    return gym


@router.get("/{gym_id}/athletes", response_model=list[AthleteListItem])
@limiter.limit("30/minute")
async def get_gym_athletes(
    request,
    gym_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
):
    query = (
        select(Athlete)
        .where(Athlete.gym_id == gym_id, Athlete.is_active == True)
        .order_by(Athlete.elo_rating.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    return result.scalars().all()
