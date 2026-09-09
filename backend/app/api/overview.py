from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Agent, SecurityEvent, Incident

router = APIRouter(
    prefix="/api/v1/system",
    tags=["system"]
)


@router.get("/overview")
def get_overview(
    db: Session = Depends(get_db)
):
    now = datetime.now(timezone.utc)

    agents = db.query(Agent).all()

    online = 0
    stale = 0
    offline = 0

    for agent in agents:
        last_seen = agent.last_seen

        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=timezone.utc)

        seconds_since_seen = (
            now - last_seen
        ).total_seconds()

        if seconds_since_seen <= 30:
            online += 1
        elif seconds_since_seen <= 120:
            stale += 1
        else:
            offline += 1

    total_events = db.query(SecurityEvent).count()

    detected_events = (
        db.query(SecurityEvent)
        .filter(SecurityEvent.detected.is_(True))
        .count()
    )

    total_incidents = db.query(Incident).count()

    open_incidents = (
        db.query(Incident)
        .filter(Incident.status == "open")
        .count()
    )

    investigating_incidents = (
        db.query(Incident)
        .filter(Incident.status == "investigating")
        .count()
    )

    resolved_incidents = (
        db.query(Incident)
        .filter(Incident.status == "resolved")
        .count()
    )

    return {
        "agents": {
            "total": len(agents),
            "online": online,
            "stale": stale,
            "offline": offline,
        },
        "events": {
            "total": total_events,
            "detected": detected_events,
        },
        "incidents": {
            "total": total_incidents,
            "open": open_incidents,
            "investigating": investigating_incidents,
            "resolved": resolved_incidents,
        },
    }