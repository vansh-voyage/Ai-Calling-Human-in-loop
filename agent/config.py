import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))


def _require(key: str) -> str:
    val = os.environ.get(key, "")
    if not val:
        raise RuntimeError(f"Missing required env var: {key}")
    return val


LIVEKIT_URL: str = os.environ.get("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY: str = os.environ.get("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET: str = os.environ.get("LIVEKIT_API_SECRET", "secret")

ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "")
DEEPGRAM_API_KEY: str = os.environ.get("DEEPGRAM_API_KEY", "")
CARTESIA_API_KEY: str = os.environ.get("CARTESIA_API_KEY", "")

BACKEND_API_URL: str = os.environ.get("BACKEND_API_URL", "http://localhost:8000")
