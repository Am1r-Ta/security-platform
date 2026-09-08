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
    agent = Agent(
        agent_id=data.get("agent_id"),
        hostname=data.get("hostname", "unknown"),
        os=data.get("os", "unknown"),
        os_version=data.get("os_version", "unknown"),
        architecture=data.get("architecture", "unknown"),
        python_version=data.get("python_version", "unknown"),
        last_seen=datetime.now(timezone.utc),
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return {
        "status": "registered",
        "agent_id": agent.agent_id,
        "hostname": agent.hostname,
    }


@router.post("/{agent_id}/heartbeat")
def heartbeat(
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
            "error": "Agent not found"
        }

    agent.last_seen = datetime.now(timezone.utc)

    db.commit()
    db.refresh(agent)

    return {
        "status": "heartbeat_received",
        "agent_id": agent.agent_id,
        "last_seen": agent.last_seen,
    }


@router.get("")
def list_agents(
    db: Session = Depends(get_db)
):
    agents = (
        db.query(Agent)
        .order_by(Agent.id.desc())
        .all()
    )

    now = datetime.now(timezone.utc)

    result = []

    for agent in agents:
        last_seen = agent.last_seen

        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=timezone.utc)

        seconds_since_seen = (
            now - last_seen
        ).total_seconds()

        if seconds_since_seen <= 30:
            status = "online"
        elif seconds_since_seen <= 120:
            status = "stale"
        else:
            status = "offline"

        result.append({
            "id": agent.id,
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