"""
LiveKit agent entry point.

Run with:
    python -m agent.main dev          # local dev (creates synthetic room)
    python -m agent.main start        # production mode

The agent joins a LiveKit room, greets the caller, and handles their questions.
Each room name is used as the caller_id for help request tracking.
"""

import logging

from livekit.agents import (
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
)
from livekit.plugins import anthropic, cartesia, deepgram, silero

from agent.config import (
    ANTHROPIC_API_KEY,
    CARTESIA_API_KEY,
    DEEPGRAM_API_KEY,
    LIVEKIT_API_KEY,
    LIVEKIT_API_SECRET,
    LIVEKIT_URL,
)
from agent.salon_agent import SalonAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


async def entrypoint(ctx: JobContext) -> None:
    await ctx.connect()
    logger.info("Agent connected to room: %s", ctx.room.name)

    # Use the room name as the caller ID (simulates a phone number / session ID)
    caller_id = ctx.room.name
    caller_name: str | None = None

    # Try to pick up the caller's display name from room participants
    for participant in ctx.room.remote_participants.values():
        if participant.name:
            caller_name = participant.name
            break

    logger.info("Caller: %s (%s)", caller_name or "unknown", caller_id)

    agent = SalonAgent(caller_id=caller_id, caller_name=caller_name)

    session = AgentSession(
        stt=deepgram.STT(api_key=DEEPGRAM_API_KEY, model="nova-3"),
        llm=anthropic.LLM(api_key=ANTHROPIC_API_KEY, model="claude-sonnet-4-6"),
        tts=cartesia.TTS(api_key=CARTESIA_API_KEY),
        vad=silero.VAD.load(),
    )

    await session.start(room=ctx.room, agent=agent)

    # Kick off the conversation with a warm greeting
    await session.generate_reply(
        instructions=(
            "Greet the caller warmly, introduce yourself as Maya from Luxe Salon & Spa, "
            "and ask how you can help them today. Keep it to 2 sentences."
        )
    )


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            ws_url=LIVEKIT_URL,
            api_key=LIVEKIT_API_KEY,
            api_secret=LIVEKIT_API_SECRET,
        )
    )
