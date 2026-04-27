"""FastAPI app with CORS and circuit routes"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from fastapi.staticfiles import StaticFiles

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


app.mount("/data", StaticFiles(directory="data"), name="data")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(circuits.router)


@app.get("/", include_in_schema=False)
def root():
    return {
        "api": "Circuit Simulation",
        "endpoints": [
            {"method": "POST", "path": "/api/v1/run", "description": "Run circuit"},
            {"method": "GET", "path": "/api/v1/status/{process_id}", "description": "Get status"}
        ]
    }


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
