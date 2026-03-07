from fastapi import APIRouter
from app.api.routes import auth, athletes, gyms, events, matches, leaderboards, social, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(athletes.router, prefix="/athletes", tags=["Athletes"])
api_router.include_router(gyms.router, prefix="/gyms", tags=["Gyms"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(matches.router, prefix="/matches", tags=["Matches"])
api_router.include_router(leaderboards.router, prefix="/leaderboards", tags=["Leaderboards"])
api_router.include_router(social.router, prefix="/social", tags=["Social"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
