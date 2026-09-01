from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import SecurityEvent
from app.detection.engine import analyze_event


router = APIRouter(
    prefix="/api/v1/events",
    tags=["events"]
)


@router.post("")
def receive_event(
    event: dict,
    db: Session = Depends(get_db)
):
    detection = analyze_event(event)

    security_event = SecurityEvent(
        agent_id=event.get("agent_id", "unknown"),
        event_type=event.get("event_type", "unknown"),
        detected=detection["detected"],
        severity=detection["severity"],
        reason=detection["reason"],
        timestamp=datetime.now(timezone.utc),
    )

    db.add(security_event)
    db.commit()
    db.refresh(security_event)

    return {
        "status": "processed",
        "event_id": security_event.id,
        "detection": detection,
    }


@router.get("")
def list_events(
    db: Session = Depends(get_db)
):
    events = (
        db.query(SecurityEvent)
        .order_by(SecurityEvent.id.desc())
        .all()
    )

    return [
        {
            "id": event.id,
            "agent_id": event.agent_id,
            "event_type": event.event_type,
            "detected": event.detected,
            "severity": event.severity,
            "reason": event.reason,
            "timestamp": event.timestamp,
        }
        for event in events
    ]