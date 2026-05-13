"""
Seeds the knowledge base with pre-loaded salon Q&As on first startup.
Runs as part of app lifespan — safe to call multiple times (upserts).
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.knowledge_service import save_answer

logger = logging.getLogger(__name__)

SALON_SEED_KB: list[tuple[str, str]] = [
    ("What are your hours", "We're open Monday through Saturday 9 AM to 7 PM, and Sunday 10 AM to 5 PM."),
    ("Where are you located", "We're at 142 Maple Street, downtown. There's free parking in the lot behind the building."),
    ("How do I book an appointment", "You can book online at luxesalon.com/book, call us at 555-0100, or just walk in."),
    ("Do you accept walk ins", "Yes, we welcome walk-ins, though appointments are recommended on weekends."),
    ("What services do you offer", "We offer haircuts, coloring, blowouts, manicures, pedicures, facials, and massages."),
    ("How much does a haircut cost", "Haircuts start at $45 for a trim and $65 and up for a full cut and style."),
    ("Do you have gift cards", "Yes! Gift cards are available in any amount, in-salon or online at luxesalon.com."),
    ("What is your cancellation policy", "We ask for 24 hours notice to cancel or reschedule. Late cancellations may incur a 50% fee."),
    ("Do you offer color services", "Yes, we offer full color, highlights, balayage, and toning. Prices vary by length and service."),
    ("Do you offer kids haircuts", "Yes, we offer kids' haircuts for children 12 and under starting at $25."),
    ("Is there parking", "Yes, free parking is available in the lot directly behind our building on Maple Street."),
    ("Do you sell hair products", "Yes, we carry a curated selection of professional hair care products including Oribe, Kerastase, and Redken."),
]


async def seed_knowledge_base(session: AsyncSession) -> None:
    seeded = 0
    for question, answer in SALON_SEED_KB:
        await save_answer(session=session, question=question, answer=answer, source="seed")
        seeded += 1
    logger.info("[seed] Knowledge base seeded with %d entries.", seeded)
