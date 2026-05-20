from fastapi import APIRouter, HTTPException
from livekit.api import AccessToken, VideoGrants

from backend.config import settings

router = APIRouter(prefix="/livekit", tags=["livekit"])


@router.get("/token")
async def get_token(room: str = "supervisor-call", identity: str = "supervisor"):
    if not settings.livekit_api_key or not settings.livekit_api_secret:
        raise HTTPException(status_code=503, detail="LiveKit credentials not configured")

    token = (
        AccessToken(settings.livekit_api_key, settings.livekit_api_secret)
        .with_identity(identity)
        .with_name(identity)
        .with_grants(VideoGrants(room_join=True, room=room))
        .to_jwt()
    )
    return {"token": token, "url": settings.livekit_url}
