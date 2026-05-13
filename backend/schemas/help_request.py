from datetime import datetime

from pydantic import BaseModel, Field


class HelpRequestCreate(BaseModel):
    caller_id: str = Field(..., description="Simulated phone number or session ID")
    caller_name: str | None = Field(None, description="Optional caller name")
    question: str = Field(..., min_length=1, description="Raw verbatim question from caller")


class ResolveRequest(BaseModel):
    answer: str = Field(..., min_length=5, description="Supervisor's answer")
    answered_by: str | None = Field(None, description="Supervisor identifier")


class HelpRequestResponse(BaseModel):
    id: int
    caller_id: str
    caller_name: str | None
    question: str
    question_normalized: str
    status: str
    answer: str | None
    answered_by: str | None
    sms_sent: bool
    created_at: datetime
    resolved_at: datetime | None
    timeout_at: datetime

    model_config = {"from_attributes": True}


class HelpRequestListResponse(BaseModel):
    items: list[HelpRequestResponse]
    total: int
    limit: int
    offset: int


class HelpRequestStats(BaseModel):
    pending: int
    resolved: int
    unresolved: int
    total: int
