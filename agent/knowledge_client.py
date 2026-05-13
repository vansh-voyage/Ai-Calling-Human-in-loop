"""
HTTP client for the backend knowledge base lookup endpoint.

Isolated so it can be mocked in tests and swapped without touching agent logic.
"""

import logging
from dataclasses import dataclass

import aiohttp

from agent.config import BACKEND_API_URL

logger = logging.getLogger(__name__)

LOOKUP_TIMEOUT = aiohttp.ClientTimeout(total=2.0)


@dataclass
class LookupResult:
    found: bool
    answer: str | None = None
    entry_id: int | None = None


async def lookup(question: str) -> LookupResult:
    """
    Calls GET /api/v1/knowledge/lookup?q=<question>.
    Returns LookupResult(found=False) on any error so the agent falls through to escalation.
    The 2-second timeout is intentional: a slow backend should not hang the call.
    """
    try:
        async with aiohttp.ClientSession(timeout=LOOKUP_TIMEOUT) as session:
            async with session.get(
                f"{BACKEND_API_URL}/api/v1/knowledge/lookup",
                params={"q": question},
            ) as resp:
                if resp.status != 200:
                    logger.warning("KB lookup returned %d for q=%r", resp.status, question)
                    return LookupResult(found=False)
                data = await resp.json()
                return LookupResult(
                    found=data.get("found", False),
                    answer=data.get("answer"),
                    entry_id=data.get("entry_id"),
                )
    except Exception as exc:
        logger.warning("KB lookup failed (%s), will escalate: %s", type(exc).__name__, exc)
        return LookupResult(found=False)
