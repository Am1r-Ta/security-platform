from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Agent


router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


@router.post("/register")
def register_agent(data: dict, db: Session = Depends(get_db)):
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
        db.commit()

        return {
            "status": "updated",
            "agent_id": existing_agent.agent_id,
        }

    agent = Agent(
        agent_id=data["agent_id"],
        hostname=data["hostname"],
        os=data["os"],
        os_version=data["os_version"],
        architecture=data["architecture"],
        python_version=data["python_version"],
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return {
        "status": "registered",
        "agent_id": agent.agent_id,
    }


@router.get("")
def list_agents(db: Session = Depends(get_db)):
    agents = db.query(Agent).all()

    return [
        {
            "agent_id": agent.agent_id,
            "hostname": agent.hostname,
            "os": agent.os,
            "os_version": agent.os_version,
            "architecture": agent.architecture,
            "python_version": agent.python_version,
        }
        for agent in agents
    ]