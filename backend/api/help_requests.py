"""
Help Requests API

GET  /help-requests          — list (filterable by status)
GET  /help-requests/stats    — count by status
GET  /help-requests/{id}     — single request
POST /help-requests          — create (called by agent on escalation)
PATCH /help-requests/{id}/resolve — supervisor submits answer
"""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session
from backend.models.help_request import HelpRequest
from backend.schemas.help_request import (
    HelpRequestCreate,
    HelpRequestListResponse,
    HelpRequestResponse,
    HelpRequestStats,
    ResolveRequest,
)
from backend.services import knowledge_service, notification_service, sms_service
from backend.services.knowledge_service import normalize_question

router = APIRouter(prefix="/help-requests", tags=["help-requests"])


@router.get("/stats", response_model=HelpRequestStats)
async def get_stats(session: Annotated[AsyncSession, Depends(get_session)]):
    rows = await session.execute(
        select(HelpRequest.status, func.count().label("cnt")).group_by(HelpRequest.status)
    )
    counts = {row.status: row.cnt for row in rows}
    pending = counts.get("pending", 0)
    resolved = counts.get("resolved", 0)
    unresolved = counts.get("unresolved", 0)
    return HelpRequestStats(
        pending=pending,
        resolved=resolved,
        unresolved=unresolved,
        total=pending + resolved + unresolved,
    )


@router.get("", response_model=HelpRequestListResponse)
async def list_requests(
    session: Annotated[AsyncSession, Depends(get_session)],
    status: str | None = Query(None, description="Filter: pending | resolved | unresolved"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    stmt = select(HelpRequest)
    count_stmt = select(func.count()).select_from(HelpRequest)

    if status:
        stmt = stmt.where(HelpRequest.status == status)
        count_stmt = count_stmt.where(HelpRequest.status == status)

    stmt = stmt.order_by(HelpRequest.created_at.desc()).limit(limit).offset(offset)

    total = (await session.execute(count_stmt)).scalar_one()
    items = list((await session.execute(stmt)).scalars().all())

    return HelpRequestListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{request_id}", response_model=HelpRequestResponse)
async def get_request(
    request_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    hr = await session.get(HelpRequest, request_id)
    if hr is None:
        raise HTTPException(404, f"No help request with id={request_id}")
    return hr


@router.post("", response_model=HelpRequestResponse, status_code=201)
async def create_request(
    body: HelpRequestCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    hr = HelpRequest(
        caller_id=body.caller_id,
        caller_name=body.caller_name,
        question=body.question,
        question_normalized=normalize_question(body.question),
    )
    session.add(hr)
    await session.commit()
    await session.refresh(hr)

    # Notify supervisor (fire-and-forget; errors are logged but do not fail the request)
    try:
        await notification_service.notify_supervisor(
            request_id=hr.id,
            caller_id=hr.caller_id,
            caller_name=hr.caller_name,
            question=hr.question,
        )
    except Exception:
        pass

    return hr


@router.patch("/{request_id}/resolve", response_model=HelpRequestResponse)
async def resolve_request(
    request_id: int,
    body: ResolveRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    hr = await session.get(HelpRequest, request_id)
    if hr is None:
        raise HTTPException(404, f"No help request with id={request_id}")
    if hr.status != "pending":
        raise HTTPException(
            409,
            f"Cannot resolve a request with status={hr.status!r}. "
            "Only 'pending' requests can be resolved.",
        )

    hr.status = "resolved"
    hr.answer = body.answer
    hr.answered_by = body.answered_by
    hr.resolved_at = datetime.now(timezone.utc).replace(tzinfo=None)
    hr.sms_sent = True

    # Save to knowledge base
    await knowledge_service.save_answer(
        session=session,
        question=hr.question,
        answer=body.answer,
        help_request_id=hr.id,
        source="supervisor",
    )

    await session.commit()
    await session.refresh(hr)

    # Simulate follow-up SMS (fire-and-forget)
    try:
        await sms_service.send_followup_sms(
            caller_id=hr.caller_id,
            caller_name=hr.caller_name,
            question=hr.question,
            answer=body.answer,
        )
    except Exception:
        pass

    return hr
