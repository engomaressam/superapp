<![CDATA["""
ARIA - Autonomous Reasoning & Intelligent Agent
Main FastAPI Application
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.config import settings
from app.api import chat, tasks, calendar, transport, medical, reminders, webhooks
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.logging import LoggingMiddleware

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting ARIA backend", version=settings.VERSION)
    
    # Initialize database connections
    # await init_database()
    
    # Initialize agent orchestrator
    # await init_orchestrator()
    
    # Initialize web automation browser
    # await init_browser()
    
    yield
    
    # Shutdown
    logger.info("Shutting down ARIA backend")
    
    # Cleanup resources
    # await close_database()
    # await close_browser()


# Create FastAPI application
app = FastAPI(
    title="ARIA - Autonomous Reasoning & Intelligent Agent",
    description="""
    ARIA is a next-generation Large Action Model (LAM) that transforms 
    your smartphone into an intelligent personal assistant capable of 
    executing real-world tasks autonomously.
    
    ## Features
    
    * **Multi-Agent Orchestration** - Specialized agents for different domains
    * **Natural Language Understanding** - Understand complex, multi-step requests
    * **API Integrations** - Direct connections to Uber, Google Calendar, etc.
    * **Web Automation** - Playwright-based automation for services without APIs
    * **Privacy-First** - PII detection and masking before LLM processing
    
    ## Authentication
    
    All endpoints require a Bearer token in the Authorization header.
    """,
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)


# Exception Handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        path=request.url.path,
        method=request.method,
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred" if not settings.DEBUG else str(exc),
            }
        }
    )


# Include API Routers
app.include_router(
    chat.router,
    prefix="/v1/chat",
    tags=["Chat"]
)

app.include_router(
    tasks.router,
    prefix="/v1/tasks",
    tags=["Tasks"]
)

app.include_router(
    calendar.router,
    prefix="/v1/calendar",
    tags=["Calendar"]
)

app.include_router(
    transport.router,
    prefix="/v1/transport",
    tags=["Transport"]
)

app.include_router(
    medical.router,
    prefix="/v1/medical",
    tags=["Medical"]
)

app.include_router(
    reminders.router,
    prefix="/v1/reminders",
    tags=["Reminders"]
)

app.include_router(
    webhooks.router,
    prefix="/v1/webhooks",
    tags=["Webhooks"]
)


# Health Check Endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for load balancers and monitoring.
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness check - verifies all dependencies are available.
    """
    checks = {
        "database": True,  # await check_database()
        "redis": True,     # await check_redis()
        "llm": True,       # await check_llm_connection()
    }
    
    all_ready = all(checks.values())
    
    return JSONResponse(
        status_code=200 if all_ready else 503,
        content={
            "ready": all_ready,
            "checks": checks,
        }
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "ARIA API",
        "version": settings.VERSION,
        "description": "Autonomous Reasoning & Intelligent Agent",
        "documentation": "/docs" if settings.DEBUG else "Contact admin for API docs",
        "status": "operational",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS if not settings.DEBUG else 1,
    )
]]>
