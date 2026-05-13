"""
Notification service: simulates texting the supervisor when a help request is created.

Always logs a structured console block.
If SUPERVISOR_WEBHOOK_URL is set, also POSTs the payload to that URL
(works with Slack incoming webhooks, Make.com scenarios, or any HTTP endpoint).
"""

import json
import logging

import httpx

from backend.config import settings

logger = logging.getLogger(__name__)


async def notify_supervisor(
    request_id: int,
    caller_id: str,
    caller_name: str | None,
    question: str,
) -> None:
    caller_label = f"{caller_name} ({caller_id})" if caller_name else caller_id

    print(
        f"\n{'='*60}\n"
        f"[SUPERVISOR ALERT] New help request #{request_id}\n"
        f"  Caller : {caller_label}\n"
        f"  Question: {question!r}\n"
        f"  Dashboard: http://localhost:5173/dashboard\n"
        f"{'='*60}\n"
    )

    if settings.supervisor_webhook_url:
        payload = {
            "text": f"Hey, I need help answering: {question!r}",
            "request_id": request_id,
            "caller": caller_label,
            "dashboard_url": "http://localhost:5173/dashboard",
        }
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    settings.supervisor_webhook_url,
                    content=json.dumps(payload),
                    headers={"Content-Type": "application/json"},
                )
                resp.raise_for_status()
                logger.info("Supervisor webhook delivered (status %s)", resp.status_code)
        except Exception as exc:
            logger.warning("Supervisor webhook failed: %s", exc)
