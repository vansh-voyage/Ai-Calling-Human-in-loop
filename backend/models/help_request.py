from datetime import datetime, timedelta, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class HelpRequest(Base):
    __tablename__ = "help_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    caller_id: Mapped[str] = mapped_column(String(64), nullable=False)
    caller_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    question_normalized: Mapped[str] = mapped_column(String(512), nullable=False, index=True)

    # Lifecycle: pending → resolved | unresolved
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    answered_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    sms_sent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    # Set at insert time so the timeout reaper can use a fast index scan
    timeout_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __init__(self, **kwargs):
        from backend.config import settings

        if "timeout_at" not in kwargs:
            created = kwargs.get("created_at") or _utcnow()
            kwargs["timeout_at"] = created + timedelta(hours=settings.request_timeout_hours)
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<HelpRequest id={self.id} status={self.status} caller={self.caller_id}>"
