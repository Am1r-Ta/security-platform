from fastapi import FastAPI
from app.api.health import router as health_router

app = FastAPI(
    title="Security Platform",
    version="0.1.0"
)

app.include_router(health_router)

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