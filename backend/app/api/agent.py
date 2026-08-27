from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/agent", tags=["Agent"])


class SystemInfo(BaseModel):
    agent_id: str
    hostname: str
    os: str
    os_version: str
    architecture: str
    python_version: str


@router.post("/system-info")
def receive_system_info(info: SystemInfo):
    return {
        "status": "received",
        "data": info.model_dump()
    }