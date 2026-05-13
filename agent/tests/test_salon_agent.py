"""
Unit tests for SalonAgent logic.
HTTP clients are mocked so no network calls are made.
"""

from unittest.mock import AsyncMock, patch

import pytest

from agent.knowledge_client import LookupResult
from agent.salon_agent import SalonAgent


class FakeRunContext:
    pass


@pytest.mark.asyncio
async def test_lookup_answer_returns_kb_answer():
    agent = SalonAgent(caller_id="+15550100")
    mock_result = LookupResult(found=True, answer="We open at 9 AM.", entry_id=1)

    with patch("agent.salon_agent.knowledge_client.lookup", new=AsyncMock(return_value=mock_result)):
        result = await agent.lookup_answer(FakeRunContext(), "What time do you open?")

    assert result == "We open at 9 AM."


@pytest.mark.asyncio
async def test_lookup_answer_escalates_when_not_found():
    agent = SalonAgent(caller_id="+15550101", caller_name="Jane Doe")
    not_found = LookupResult(found=False)

    from agent.escalation_client import HelpRequestResult

    mock_hr = HelpRequestResult(id=42, status="pending", timeout_at="2026-05-14T10:00:00")

    with (
        patch("agent.salon_agent.knowledge_client.lookup", new=AsyncMock(return_value=not_found)),
        patch(
            "agent.salon_agent.escalation_client.create_help_request",
            new=AsyncMock(return_value=mock_hr),
        ),
    ):
        result = await agent.lookup_answer(FakeRunContext(), "Do you offer hot stone massage?")

    assert "ESCALATED" in result
    assert "follow up" in result.lower()


@pytest.mark.asyncio
async def test_lookup_answer_escalates_gracefully_when_backend_down():
    agent = SalonAgent(caller_id="+15550102")
    not_found = LookupResult(found=False)

    with (
        patch("agent.salon_agent.knowledge_client.lookup", new=AsyncMock(return_value=not_found)),
        patch(
            "agent.salon_agent.escalation_client.create_help_request",
            new=AsyncMock(return_value=None),  # backend is down
        ),
    ):
        result = await agent.lookup_answer(FakeRunContext(), "Do you do IV drips?")

    # Should still return a usable message even when DB write failed
    assert "ESCALATED" in result


@pytest.mark.asyncio
async def test_end_call_returns_goodbye():
    agent = SalonAgent(caller_id="+15550103")
    result = await agent.end_call(FakeRunContext())
    assert "CALL_ENDED" in result
    assert "goodbye" in result.lower() or "Luxe Salon" in result
