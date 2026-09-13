def analyze_process_event(event: dict) -> dict | None:
    event_type = event.get("event_type")

    if event_type != "new_process":
        return None

    process_name = (
        event.get("process_name") or ""
    ).lower()

    if process_name in {
        "powershell.exe",
        "cmd.exe",
    }:
        return {
            "detected": False,
            "severity": "low",
            "reason": "Command-line process observed",
        }

    return {
        "detected": False,
        "severity": "low",
        "reason": "New process observed",
    }