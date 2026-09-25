from app.db.database import SessionLocal
from app.db.models import (
    Incident,
    IncidentEvent,
    SecurityEvent,
)


def backfill_incident_events():
    db = SessionLocal()

    try:
        incidents = (
            db.query(Incident)
            .order_by(Incident.id.asc())
            .all()
        )

        added = 0

        for incident in incidents:
            if incident.event_id is None:
                continue

            trigger_event = (
                db.query(SecurityEvent)
                .filter(
                    SecurityEvent.id == incident.event_id
                )
                .first()
            )

            if not trigger_event:
                continue

            existing = (
                db.query(IncidentEvent)
                .filter(
                    IncidentEvent.incident_id == incident.id,
                    IncidentEvent.event_id == trigger_event.id,
                )
                .first()
            )

            if existing:
                continue

            db.add(
                IncidentEvent(
                    incident_id=incident.id,
                    event_id=trigger_event.id,
                )
            )

            added += 1

        db.commit()

        print(
            f"Backfill complete. Added {added} "
            "incident-event associations."
        )

    finally:
        db.close()


if __name__ == "__main__":
    backfill_incident_events()