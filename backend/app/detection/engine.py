from app.detection.rules.authentication import (
    analyze_authentication_event,
)

from app.detection.rules.process import (
    analyze_process_event,
)


def analyze_event(event: dict) -> dict:
    rules = [
        analyze_authentication_event,
        analyze_process_event,
    ]

    for rule in rules:
        result = rule(event)

        if result is not None:
            return result

    return {
        "detected": False,
        "severity": "low",
        "reason": None,
        "rule_id": None,
    }