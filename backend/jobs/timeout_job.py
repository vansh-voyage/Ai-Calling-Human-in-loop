"""
Timeout reaper job.

Runs every hour via APScheduler.
Finds all help_requests where status='pending' and timeout_at < now(),
marks them 'unresolved'.

The job is idempotent — safe to run multiple times without side effects.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import update

from backend.database import get_session_context
from backend.models.help_request import HelpRequest

logger = logging.getLogger(__name__)


async def mark_timed_out_requests() -> int:
    """
    Returns the number of requests that were marked unresolved.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    async with get_session_context() as session:
        result = await session.execute(
            update(HelpRequest)
            .where(
                HelpRequest.status == "pending",
                HelpRequest.timeout_at < now,
            )
            .values(status="unresolved")
            .returning(HelpRequest.id)
        )
        timed_out_ids = [row[0] for row in result.fetchall()]
        await session.commit()

    count = len(timed_out_ids)
    if count > 0:
        logger.info("[timeout_job] Marked %d request(s) unresolved: %s", count, timed_out_ids)
    else:
        logger.debug("[timeout_job] No requests timed out.")

    return count
