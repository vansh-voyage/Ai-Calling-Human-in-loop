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
from livekit.agents.voice.room_io import RoomOptions
from livekit.plugins import cartesia, deepgram, google
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from agent.config import (
    CARTESIA_API_KEY,
    DEEPGRAM_API_KEY,
    GOOGLE_API_KEY,
    LIVEKIT_API_KEY,
    LIVEKIT_API_SECRET,
    LIVEKIT_URL,
)
from agent.salon_agent import SalonAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logging.getLogger("livekit.plugins.deepgram").setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)


async def entrypoint(ctx: JobContext) -> None:
    await ctx.connect()
    logger.info("Agent connected to room: %s", ctx.room.name)

    caller_id = ctx.room.name

    # Properly subscribe to the participant's audio track using the recommended API
    participant = await ctx.wait_for_participant()
    caller_name: str | None = participant.name or None

    logger.info("Caller: %s (%s)", caller_name or "unknown", caller_id)

    agent = SalonAgent(caller_id=caller_id, caller_name=caller_name)

    session = AgentSession(
        stt=deepgram.STT(api_key=DEEPGRAM_API_KEY, model="nova-3", language="en-US"),
        llm=google.LLM(api_key=GOOGLE_API_KEY, model="gemini-2.0-flash"),
        tts=cartesia.TTS(api_key=CARTESIA_API_KEY),
        turn_detection=MultilingualModel(),
    )

    @session.on("user_input_transcribed")
    def on_user_transcript(ev) -> None:
        if ev.is_final:
            logger.info("[USER ] %s", ev.transcript)

    @session.on("conversation_item_added")
    def on_item_added(ev) -> None:
        item = ev.item
        role = getattr(item, "role", None)
        if role == "user":
            return
        content = getattr(item, "content", None)
        if not content:
            return
        text = content if isinstance(content, str) else " ".join(
            str(c) for c in content if isinstance(c, str)
        )
        if text.strip():
            logger.info("[MAYA ] %s", text)

    await session.start(
        agent,
        room=ctx.room,
        room_options=RoomOptions(participant_identity=participant.identity),
    )
    await session.generate_reply(
        instructions="Greet the caller warmly. Say something like: "
        "'Hi! Welcome to Luxe Salon & Spa, I'm Maya your receptionist — how can I help you today?'"
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
