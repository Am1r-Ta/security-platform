from pathlib import Path
import uuid


IDENTITY_FILE = Path(__file__).resolve().parent.parent / ".agent_id"


def get_agent_id() -> str:
    if IDENTITY_FILE.exists():
        return IDENTITY_FILE.read_text(encoding="utf-8").strip()

    agent_id = str(uuid.uuid4())

    IDENTITY_FILE.write_text(
        agent_id,
        encoding="utf-8"
    )

    return agent_id