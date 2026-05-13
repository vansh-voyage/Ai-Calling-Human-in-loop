"""
HTTP client for creating help requests in the backend.

Isolated for testability — unit tests mock this module rather than HTTP.
"""

import logging
from dataclasses import dataclass

import aiohttp

from agent.config import BACKEND_API_URL

logger = logging.getLogger(__name__)

CREATE_TIMEOUT = aiohttp.ClientTimeout(total=5.0)


@dataclass
class HelpRequestResult:
    id: int
    status: str
    timeout_at: str


async def create_help_request(
    caller_id: str,
    question: str,
    caller_name: str | None = None,
) -> HelpRequestResult | None:
    """
    POST /api/v1/help-requests.
    Returns None on failure — the agent handles this gracefully by
    still telling the caller we'll follow up, even if the DB write failed.
    """
    payload = {"caller_id": caller_id, "question": question}
    if caller_name:
        payload["caller_name"] = caller_name

    try:
        async with aiohttp.ClientSession(timeout=CREATE_TIMEOUT) as session:
            async with session.post(
                f"{BACKEND_API_URL}/api/v1/help-requests",
                json=payload,
            ) as resp:
                if resp.status != 201:
                    logger.error(
                        "Failed to create help request (status %d) for q=%r", resp.status, question
                    )
                    return None
                data = await resp.json()
                logger.info("Help request #%d created for caller %s", data["id"], caller_id)
                return HelpRequestResult(
                    id=data["id"],
                    status=data["status"],
                    timeout_at=data["timeout_at"],
                )
    except Exception as exc:
        logger.error("Escalation failed (%s): %s", type(exc).__name__, exc)
        return None
