from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import SecurityEvent, Incident
from app.detection.engine import analyze_event


router = APIRouter(
    prefix="/api/v1/events",
    tags=["events"]
)


@router.post("")
def receive_event(event: dict, db: Session = Depends(get_db)):
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

    incident_id = None

    if detection["detected"]:
        incident = Incident(
            event_id=security_event.id,
            agent_id=security_event.agent_id,
            title=detection["reason"] or "Security incident detected",
            severity=detection["severity"],
            status="open",
            created_at=datetime.now(timezone.utc),
        )

        db.add(incident)
        db.commit()
        db.refresh(incident)

        incident_id = incident.id

    return {
        "status": "processed",
        "event_id": security_event.id,
        "incident_id": incident_id,
        "detection": detection,
    }


@router.get("")
def list_events(db: Session = Depends(get_db)):
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


@router.get("/incidents")
def list_incidents(db: Session = Depends(get_db)):
    incidents = (
        db.query(Incident)
        .order_by(Incident.id.desc())
        .all()
    )

    return [
        {
            "id": incident.id,
            "event_id": incident.event_id,
            "agent_id": incident.agent_id,
            "title": incident.title,
            "severity": incident.severity,
            "status": incident.status,
            "created_at": incident.created_at,
        }
        for incident in incidents
    ]


@router.patch("/incidents/{incident_id}")
def update_incident(
    incident_id: int,
    status: str,
    db: Session = Depends(get_db),
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        return {"error": "Incident not found"}

    allowed_statuses = {
        "open",
        "investigating",
        "resolved",
    }

    if status not in allowed_statuses:
        return {
            "error": "Invalid status",
            "allowed": list(allowed_statuses),
        }

    incident.status = status
    db.commit()
    db.refresh(incident)

    return {
        "status": "updated",
        "incident": {
            "id": incident.id,
            "event_id": incident.event_id,
            "agent_id": incident.agent_id,
            "title": incident.title,
            "severity": incident.severity,
            "status": incident.status,
            "created_at": incident.created_at,
        },
    }