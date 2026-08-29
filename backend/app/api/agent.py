from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Agent


router = APIRouter(
    prefix="/api/v1/agents",
    tags=["agents"]
)


@router.post("/register")
def register_agent(
    data: dict,
    db: Session = Depends(get_db)
):
    existing_agent = (
        db.query(Agent)
        .filter(Agent.agent_id == data["agent_id"])
        .first()
    )

    if existing_agent:
        existing_agent.hostname = data["hostname"]
        existing_agent.os = data["os"]
        existing_agent.os_version = data["os_version"]
        existing_agent.architecture = data["architecture"]
        existing_agent.python_version = data["python_version"]
        existing_agent.last_seen = datetime.now(timezone.utc)

        db.commit()

        return {
            "status": "updated",
            "agent_id": existing_agent.agent_id,
            "last_seen": existing_agent.last_seen,
        }

    agent = Agent(
        agent_id=data["agent_id"],
        hostname=data["hostname"],
        os=data["os"],
        os_version=data["os_version"],
        architecture=data["architecture"],
        python_version=data["python_version"],
        last_seen=datetime.now(timezone.utc),
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return {
        "status": "registered",
        "agent_id": agent.agent_id,
        "last_seen": agent.last_seen,
    }


@router.post("/{agent_id}/heartbeat")
def agent_heartbeat(
    agent_id: str,
    db: Session = Depends(get_db)
):
    agent = (
        db.query(Agent)
        .filter(Agent.agent_id == agent_id)
        .first()
    )

    if not agent:
        return {
            "status": "error",
            "message": "Agent not found"
        }

    agent.last_seen = datetime.now(timezone.utc)

    db.commit()

    return {
        "status": "heartbeat_received",
        "agent_id": agent.agent_id,
        "last_seen": agent.last_seen,
    }


@router.get("")
def list_agents(db: Session = Depends(get_db)):
    agents = db.query(Agent).all()

    now = datetime.now(timezone.utc)

    result = []

    for agent in agents:
        last_seen = agent.last_seen

        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=timezone.utc)

        seconds_since_seen = (
            now - last_seen
        ).total_seconds()

        status = "online" if seconds_since_seen <= 60 else "offline"

        result.append({
            "agent_id": agent.agent_id,
            "hostname": agent.hostname,
            "os": agent.os,
            "os_version": agent.os_version,
            "architecture": agent.architecture,
            "python_version": agent.python_version,
            "last_seen": agent.last_seen,
            "status": status,
        })

    return result