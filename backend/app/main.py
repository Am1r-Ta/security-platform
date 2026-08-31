from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.system import router as system_router
from app.api.agent import router as agent_router  
from app.db.database import Base, engine
from app.api.events import router as events_router
from app.db import models  

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Security Platform",
    version="0.1.0"
)

app.include_router(health_router)
app.include_router(system_router)
app.include_router(agent_router)
app.include_router(events_router)

@app.get("/health")
def health_check():
    return{"stutus": "ok"}
@app.get("/info")
def info_check():
    return{"project": "Security Platform","version": "0.1.0"}
@app.get("/api/v1/system/status")
def path_check():
    return{"status": "online",
        "service": "security-platform-backend",
        "version": "0.1.0"}