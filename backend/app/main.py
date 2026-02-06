"""Minimal FastAPI app"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from app.api import circuits
from app.core.config import settings

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 API Starting...")
    yield
    logger.info("👋 API Shutdown")


app = FastAPI(title="Circuit Simulation API", version="1.0", lifespan=lifespan)

# Include router
app.include_router(circuits.router)


@app.get("/")
def root():
    return {
        "api": "Circuit Simulation",
        "endpoints": [
            {"method": "POST", "path": "/api/v1/run", "description": "Run circuit"},
            {"method": "GET", "path": "/api/v1/status/{process_id}", "description": "Get status"}
        ]
    }


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
