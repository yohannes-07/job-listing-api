from fastapi import APIRouter
from . import auth, jobs, me

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(me.router, prefix="/me", tags=["me"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])
