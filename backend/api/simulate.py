"""
Simulate endpoint — POST /simulate/call

Allows testing the full escalation flow without a running LiveKit agent.
It replicates exactly what the agent does:
  1. Check knowledge base
  2. If found → return answer directly
  3. If not found → create help_request + notify supervisor
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session
from backend.models.help_request import HelpRequest
from backend.schemas.help_request import HelpRequestResponse
from backend.services import knowledge_service, notification_service
from backend.services.knowledge_service import normalize_question

router = APIRouter(prefix="/simulate", tags=["simulate"])


class SimulateCallRequest(BaseModel):
    caller_id: str = Field(..., description="Simulated phone number, e.g. '+15550100'")
    caller_name: str | None = None
    question: str = Field(..., min_length=1)


class SimulateCallResponse(BaseModel):
    escalated: bool
    answer: str | None = None
    help_request: HelpRequestResponse | None = None
    message: str


@router.post("/call", response_model=SimulateCallResponse)
async def simulate_call(
    body: SimulateCallRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    # Step 1: check knowledge base
    entry = await knowledge_service.lookup_answer(session, body.question)
    if entry is not None:
        return SimulateCallResponse(
            escalated=False,
            answer=entry.answer,
            message=f"KB hit (entry #{entry.id}, served {entry.lookup_count} times). "
                    f"Agent would respond directly.",
        )

    # Step 2: escalate — create help request
    hr = HelpRequest(
        caller_id=body.caller_id,
        caller_name=body.caller_name,
        question=body.question,
        question_normalized=normalize_question(body.question),
    )
    session.add(hr)
    await session.commit()
    await session.refresh(hr)

    try:
        await notification_service.notify_supervisor(
            request_id=hr.id,
            caller_id=hr.caller_id,
            caller_name=hr.caller_name,
            question=hr.question,
        )
    except Exception:
        pass

    return SimulateCallResponse(
        escalated=True,
        help_request=HelpRequestResponse.model_validate(hr),
        message="No KB answer found. Help request created and supervisor notified.",
    )
