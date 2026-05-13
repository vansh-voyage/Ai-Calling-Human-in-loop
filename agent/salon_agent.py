"""
SalonAgent — the LiveKit voice agent for Luxe Salon & Spa.

Persona: Maya, a friendly and knowledgeable salon receptionist.

Decision logic:
  1. Always call lookup_answer before answering any salon-specific question.
  2. If the KB has an answer, return it to the LLM to speak naturally.
  3. If not, escalate: create a help_request and tell the caller we'll follow up.
  4. Call end_call when the caller is done.
"""

import logging

from livekit.agents import Agent, RunContext, function_tool

from agent import escalation_client, knowledge_client

logger = logging.getLogger(__name__)

SALON_SYSTEM_PROMPT = """
You are Maya, the warm and professional receptionist at Luxe Salon & Spa.
Your job is to assist callers with questions about our services, pricing,
availability, hours, location, and general salon information.

RULES — follow these exactly:
1. For ANY question about the salon (services, prices, hours, location, policies, staff,
   products, bookings), ALWAYS call `lookup_answer` first — never answer from memory alone.
2. If `lookup_answer` returns an answer, use it to compose your response naturally.
   Keep your spoken reply under 3 sentences for voice clarity.
3. If `lookup_answer` returns an ESCALATED message, deliver the follow-up text
   naturally and warmly — do not read it verbatim.
4. Never make up prices, hours, staff names, or services.
5. If a caller asks something unrelated to the salon (e.g. the weather), politely
   redirect: "I can help with questions about Luxe Salon. What can I assist you with?"
6. When the caller says goodbye or indicates they are finished, call `end_call`.
7. Keep a warm, upbeat, professional tone at all times.

Salon overview (do NOT use these as answers — always go through lookup_answer):
- Name: Luxe Salon & Spa, 142 Maple Street
- We are a full-service salon: hair, nails, facials, massage
""".strip()


class SalonAgent(Agent):
    def __init__(self, caller_id: str, caller_name: str | None = None) -> None:
        super().__init__(instructions=SALON_SYSTEM_PROMPT)
        self.caller_id = caller_id
        self.caller_name = caller_name

    @function_tool
    async def lookup_answer(self, context: RunContext, question: str) -> str:
        """
        Look up an answer in the Luxe Salon knowledge base.

        Call this for ANY question about salon services, prices, hours,
        location, booking, policies, staff, or products.
        Always call this BEFORE attempting to answer salon questions yourself.

        Args:
            question: The caller's question, in their own words.
        """
        result = await knowledge_client.lookup(question)

        if result.found and result.answer:
            logger.info(
                "KB hit (entry #%s) for caller %s: %r",
                result.entry_id,
                self.caller_id,
                question,
            )
            return result.answer

        # Not in KB — escalate to supervisor
        return await self._escalate(question)

    async def _escalate(self, question: str) -> str:
        """
        Creates a help_request in the backend and returns the string
        the LLM will use to compose the spoken follow-up message.
        """
        help_req = await escalation_client.create_help_request(
            caller_id=self.caller_id,
            question=question,
            caller_name=self.caller_name,
        )

        if help_req is not None:
            logger.info(
                "Escalated to supervisor: help_request #%d for caller %s",
                help_req.id,
                self.caller_id,
            )
        else:
            logger.error(
                "Escalation DB write failed for caller %s. Caller will still hear follow-up message.",
                self.caller_id,
            )

        caller_first = self.caller_name.split()[0] if self.caller_name else ""
        greeting = f", {caller_first}" if caller_first else ""

        return (
            f"ESCALATED: Tell the caller{greeting}: "
            "'That's a great question — I want to make sure I give you the right information. "
            "Let me check with my team and someone will follow up with you shortly. "
            "Is there anything else I can help you with today?'"
        )

    @function_tool
    async def end_call(self, context: RunContext) -> str:
        """
        Gracefully end the call when the caller says goodbye or indicates they are done.
        Call this when you hear 'goodbye', 'thank you, bye', 'that's all', or similar.
        """
        logger.info("Call ended for caller %s", self.caller_id)
        return "CALL_ENDED: Say a warm goodbye and thank them for calling Luxe Salon."
