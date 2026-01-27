"""
FastAPI Main Application
AI-Driven Sky130 ASIC Platform
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from app.core.config import settings
from app.api import circuits, simulate, layout, verify, optimize, jobs

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Create necessary directories
    Path(settings.WORK_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.RESULTS_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.CACHE_DIR).mkdir(parents=True, exist_ok=True)
    Path("./logs").mkdir(parents=True, exist_ok=True)
    
    logger.info(f"📦 PDK: {settings.PDK_NAME} at {settings.SKY130_PDK}")
    logger.info(f"🔧 Tools: Ngspice, Magic, KLayout, Netgen")
    logger.info(f"🧠 AI Engine: {'Enabled' if settings.AI_ENABLED else 'Disabled'}")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down platform...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered analog IC design automation platform using Sky130 PDK",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Root & Health Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Platform information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "pdk": settings.PDK_NAME,
        "status": "operational",
        "endpoints": {
            "circuits": f"{settings.API_V1_PREFIX}/circuits",
            "simulate": f"{settings.API_V1_PREFIX}/simulate",
            "layout": f"{settings.API_V1_PREFIX}/layout",
            "verify": f"{settings.API_V1_PREFIX}/verify",
            "optimize": f"{settings.API_V1_PREFIX}/optimize",
            "jobs": f"{settings.API_V1_PREFIX}/jobs",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "pdk_available": Path(settings.SKY130_PDK).exists(),
        "work_dir": Path(settings.WORK_DIR).exists(),
    }


@app.get(f"{settings.API_V1_PREFIX}/info")
async def platform_info():
    """Detailed platform information"""
    return {
        "platform": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "debug": settings.DEBUG,
        },
        "pdk": {
            "name": settings.PDK_NAME,
            "root": settings.PDK_ROOT,
            "path": settings.SKY130_PDK,
            "available": Path(settings.SKY130_PDK).exists(),
        },
        "tools": {
            "ngspice": settings.NGSPICE_BIN,
            "magic": settings.MAGIC_BIN,
            "netgen": settings.NETGEN_BIN,
            "klayout": settings.KLAYOUT_BIN,
        },
        "ai_engine": {
            "enabled": settings.AI_ENABLED,
            "max_iterations": settings.MAX_OPTIMIZATION_ITERATIONS,
        }
    }


# ============================================================================
# API Routes
# ============================================================================

# Include API routers (will be implemented)
# app.include_router(circuits.router, prefix=f"{settings.API_V1_PREFIX}/circuits", tags=["circuits"])
# app.include_router(simulate.router, prefix=f"{settings.API_V1_PREFIX}/simulate", tags=["simulate"])
# app.include_router(layout.router, prefix=f"{settings.API_V1_PREFIX}/layout", tags=["layout"])
# app.include_router(verify.router, prefix=f"{settings.API_V1_PREFIX}/verify", tags=["verify"])
# app.include_router(optimize.router, prefix=f"{settings.API_V1_PREFIX}/optimize", tags=["optimize"])
# app.include_router(jobs.router, prefix=f"{settings.API_V1_PREFIX}/jobs", tags=["jobs"])


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
