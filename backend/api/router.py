from fastapi import APIRouter

from backend.api import help_requests, knowledge, livekit, simulate

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(help_requests.router)
api_router.include_router(knowledge.router)
api_router.include_router(simulate.router)
api_router.include_router(livekit.router)
