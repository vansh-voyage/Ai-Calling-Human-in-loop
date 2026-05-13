"""
SMS service: simulates texting the original caller back with the supervisor's answer.

Always logs a structured console block.
If SMS_WEBHOOK_URL is set, also POSTs the payload (useful for Slack/webhook testing).
"""

import json
import logging

import httpx

from backend.config import settings

logger = logging.getLogger(__name__)


async def send_followup_sms(
    caller_id: str,
    caller_name: str | None,
    question: str,
    answer: str,
) -> None:
    caller_label = f"{caller_name} ({caller_id})" if caller_name else caller_id
    message = (
        f"Hi{' ' + caller_name if caller_name else ''}! "
        f"Following up from your call — you asked: {question!r}. "
        f"Here's the answer: {answer}"
    )

    print(
        f"\n{'='*60}\n"
        f"[SMS SIMULATION] → {caller_label}\n"
        f"  Re     : {question!r}\n"
        f"  Message: {message}\n"
        f"{'='*60}\n"
    )

    if settings.sms_webhook_url:
        payload = {
            "to": caller_id,
            "caller_name": caller_name,
            "re_question": question,
            "message": message,
        }
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    settings.sms_webhook_url,
                    content=json.dumps(payload),
                    headers={"Content-Type": "application/json"},
                )
                resp.raise_for_status()
                logger.info("SMS webhook delivered (status %s)", resp.status_code)
        except Exception as exc:
            logger.warning("SMS webhook failed: %s", exc)
