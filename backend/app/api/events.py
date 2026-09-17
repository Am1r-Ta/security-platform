from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import (
    SecurityEvent,
    Incident,
    IncidentTimeline,
)
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
        pid=event.get("pid"),
        process_name=event.get("process_name"),
        detected=detection["detected"],
        severity=detection["severity"],
        reason=detection["reason"],
        rule_id=detection["rule_id"],
        timestamp=datetime.now(timezone.utc),
    )

    db.add(security_event)
    db.commit()
    db.refresh(security_event)

    incident_id = None
    incident_created = False
    incident_reused = False

    if detection["detected"]:
        agent_id = security_event.agent_id
        rule_id = detection["rule_id"]
        event_type = security_event.event_type

        active_incident = (
            db.query(Incident)
            .filter(
                Incident.agent_id == agent_id,
                Incident.rule_id == rule_id,
                Incident.event_id.is_not(None),
                Incident.status.in_(
                    ["open", "investigating"]
                ),
            )
            .order_by(Incident.id.desc())
            .first()
        )

        if active_incident:
            incident_id = active_incident.id
            incident_reused = True

        else:
            incident = Incident(
                event_id=security_event.id,
                agent_id=agent_id,
                title=(
                    detection["reason"]
                    or "Security incident detected"
                ),
                severity=detection["severity"],
                status="open",
                rule_id=rule_id,
                created_at=datetime.now(timezone.utc),
            )

            db.add(incident)
            db.commit()
            db.refresh(incident)

            timeline_entry = IncidentTimeline(
                incident_id=incident.id,
                action="incident_created",
                old_status=None,
                new_status=incident.status,
                timestamp=datetime.now(timezone.utc),
            )

            db.add(timeline_entry)
            db.commit()

            incident_id = incident.id
            incident_created = True

    return {
        "status": "processed",
        "event_id": security_event.id,
        "incident_id": incident_id,
        "incident_created": incident_created,
        "incident_reused": incident_reused,
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
            "pid": event.pid,
            "process_name": event.process_name,
            "detected": event.detected,
            "severity": event.severity,
            "reason": event.reason,
            "rule_id": event.rule_id,
            "timestamp": event.timestamp,
        }
        for event in events
    ]


@router.get("/incidents")
def list_incidents(
    status: str | None = None,
    severity: str | None = None,
    rule_id: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Incident)

    if status is not None:
        query = query.filter(
            Incident.status == status
        )

    if severity is not None:
        query = query.filter(
            Incident.severity == severity
        )

    if rule_id is not None:
        query = query.filter(
            Incident.rule_id == rule_id
        )

    incidents = (
        query
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
            "rule_id": incident.rule_id,
            "created_at": incident.created_at,
        }
        for incident in incidents
    ]


@router.get("/incidents/{incident_id}")
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        return {
            "error": "Incident not found"
        }

    event = (
        db.query(SecurityEvent)
        .filter(SecurityEvent.id == incident.event_id)
        .first()
    )

    timeline = (
        db.query(IncidentTimeline)
        .filter(
            IncidentTimeline.incident_id == incident.id
        )
        .order_by(IncidentTimeline.id.asc())
        .all()
    )

    return {
        "id": incident.id,
        "event_id": incident.event_id,
        "agent_id": incident.agent_id,
        "title": incident.title,
        "severity": incident.severity,
        "status": incident.status,
        "rule_id": incident.rule_id,
        "created_at": incident.created_at,
        "event": {
            "id": event.id,
            "agent_id": event.agent_id,
            "event_type": event.event_type,
            "pid": event.pid,
            "process_name": event.process_name,
            "detected": event.detected,
            "severity": event.severity,
            "reason": event.reason,
            "rule_id": event.rule_id,
            "timestamp": event.timestamp,
        } if event else None,
        "timeline": [
            {
                "id": item.id,
                "action": item.action,
                "old_status": item.old_status,
                "new_status": item.new_status,
                "timestamp": item.timestamp,
            }
            for item in timeline
        ],
    }


@router.get("/incidents/{incident_id}/timeline")
def get_incident_timeline(
    incident_id: int,
    db: Session = Depends(get_db)
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        return {
            "error": "Incident not found"
        }

    timeline = (
        db.query(IncidentTimeline)
        .filter(
            IncidentTimeline.incident_id == incident_id
        )
        .order_by(IncidentTimeline.id.asc())
        .all()
    )

    return [
        {
            "id": item.id,
            "incident_id": item.incident_id,
            "action": item.action,
            "old_status": item.old_status,
            "new_status": item.new_status,
            "timestamp": item.timestamp,
        }
        for item in timeline
    ]


@router.patch("/incidents/{incident_id}")
def update_incident(
    incident_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        return {
            "error": "Incident not found"
        }

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

    old_status = incident.status

    if old_status != status:
        incident.status = status

        timeline_entry = IncidentTimeline(
            incident_id=incident.id,
            action="status_changed",
            old_status=old_status,
            new_status=status,
            timestamp=datetime.now(timezone.utc),
        )

        db.add(timeline_entry)

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
            "rule_id": incident.rule_id,
            "created_at": incident.created_at,
        },
    }