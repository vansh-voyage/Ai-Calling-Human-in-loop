from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class KnowledgeEntry(Base):
    __tablename__ = "knowledge_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Normalized question is the stable lookup key — unique across the table
    question_normalized: Mapped[str] = mapped_column(
        String(512), nullable=False, unique=True, index=True
    )
    question_display: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)

    # source: "supervisor" (from a resolved help request) or "seed" (pre-loaded)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="supervisor")

    # Lineage: which help_request originated this entry (nullable for seeded entries)
    help_request_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("help_requests.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)

    # Accumulates every time this entry answers a question without escalation
    lookup_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return f"<KnowledgeEntry id={self.id} q={self.question_normalized[:40]!r}>"
