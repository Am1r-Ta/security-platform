def analyze_authentication_event(event: dict) -> dict | None:
    event_type = event.get("event_type")

    if event_type == "failed_login":
        return {
            "detected": True,
            "severity": "medium",
            "reason": "Failed login attempt detected",
            "rule_id": "AUTH-001",
        }

    if event_type == "multiple_failed_logins":
        return {
            "detected": True,
            "severity": "high",
            "reason": "Multiple failed login attempts detected",
            "rule_id": "AUTH-002",
        }

    return None