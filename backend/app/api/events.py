from fastapi import APIRouter

from app.detection.engine import analyze_event


router = APIRouter(
    prefix="/api/v1/events",
    tags=["events"]
)


@router.post("")
def receive_event(event: dict):
    detection = analyze_event(event)

    return {
        "status": "processed",
        "event": event,
        "detection": detection,
    }