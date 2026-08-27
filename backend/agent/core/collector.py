import platform
import uuid


AGENT_ID = str(uuid.uuid4())


def collect_system_info():
    return {
        "agent_id": AGENT_ID,
        "hostname": platform.node(),
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
    }