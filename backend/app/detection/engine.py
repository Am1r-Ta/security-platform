def analyze_event(event: dict) -> dict:
    event_type = event.get("event_type", "")
    process_name = (event.get("process_name") or "").lower()

    severity = "low"
    detected = False
    reason = None

    # Authentication rules
    if event_type == "failed_login":
        detected = True
        severity = "medium"
        reason = "Failed login attempt detected"

    elif event_type == "multiple_failed_logins":
        detected = True
        severity = "high"
        reason = "Multiple failed login attempts detected"

    # Process telemetry
    elif event_type == "new_process":
        severity = "low"
        reason = "New process observed"

        if process_name in {"powershell.exe", "cmd.exe"}:
            severity = "low"
            reason = "Command-line process observed"

    return {
        "detected": detected,
        "severity": severity,
        "reason": reason,
    }