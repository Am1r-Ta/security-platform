def analyze_event(event: dict) -> dict:
    event_type = event.get("event_type", "")
    severity = "low"
    detected = False
    reason = None

    if event_type == "failed_login":
        detected = True
        severity = "medium"
        reason = "Failed login attempt detected"

    elif event_type == "multiple_failed_logins":
        detected = True
        severity = "high"
        reason = "Multiple failed login attempts detected"

    elif event_type == "new_process":
        severity = "low"
        reason = "New process observed"

    return {
        "detected": detected,
        "severity": severity,
        "reason": reason,
    }