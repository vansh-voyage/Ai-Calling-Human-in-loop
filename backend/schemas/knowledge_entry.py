from datetime import datetime

from pydantic import BaseModel, Field


class KnowledgeEntryCreate(BaseModel):
    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)
    source: str = Field(default="seed")


class KnowledgeEntryUpdate(BaseModel):
    answer: str = Field(..., min_length=5)


class KnowledgeEntryResponse(BaseModel):
    id: int
    question_normalized: str
    question_display: str
    answer: str
    source: str
    help_request_id: int | None
    created_at: datetime
    updated_at: datetime
    lookup_count: int

    model_config = {"from_attributes": True}


class KnowledgeEntryListResponse(BaseModel):
    items: list[KnowledgeEntryResponse]
    total: int
    limit: int
    offset: int


class KnowledgeLookupResponse(BaseModel):
    found: bool
    answer: str | None = None
    entry_id: int | None = None
