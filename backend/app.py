"""
FastAPI Application for Project Delay Risk AI.

Provides REST API endpoints for:
- Risk analysis
- What-if scenario simulation
- Health checks

Security:
- API key authentication (optional, enabled via environment variable)
- CORS configuration
- Rate limiting
- Structured error responses
"""

import os
import time
from typing import Optional, Dict
from collections import defaultdict

from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.schemas import AnalyzeRequest, AnalyzeResponse
from backend.services.analysis_service import (
    run_analysis, clear_model_cache, 
    get_analysis_history, get_analysis_by_id, get_stats
)
from backend.core.exceptions import (
    BaseAppError, AnalysisError, ValidationError, ScenarioNotFoundError
)
from backend.core.logging_config import setup_logging, log_request, logger
from backend.core.metrics import get_metrics, get_content_type, record_request, record_error


# Application Version - Single source of truth
APP_VERSION = "2.1.0"
APP_NAME = "Project Delay Risk AI"

# Configuration from environment
API_KEY = os.getenv("API_KEY", None)  # None = authentication disabled
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))  # requests per window
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

# Rate limiting storage (in-memory, resets on restart)
# In production, use Redis for distributed rate limiting
rate_limit_data: Dict[str, list] = defaultdict(list)

# Setup logging
setup_logging(level=LOG_LEVEL)

# Create FastAPI app
app = FastAPI(
    title=APP_NAME,
    description="AI-powered project delay risk and decision support system",
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include import routes
from backend.api.import_routes import router as import_router
app.include_router(import_router)


# =============================================================================
# Rate Limiting
# =============================================================================

def _check_rate_limit(client_ip: str) -> bool:
    """
    Checks if client has exceeded rate limit.
    
    Returns True if rate limit exceeded, False otherwise.
    """
    if RATE_LIMIT_REQUESTS <= 0:
        return False  # Rate limiting disabled
    
    current_time = time.time()
    window_start = current_time - RATE_LIMIT_WINDOW
    
    # Clean old entries
    rate_limit_data[client_ip] = [
        t for t in rate_limit_data[client_ip] if t > window_start
    ]
    
    # Check limit
    if len(rate_limit_data[client_ip]) >= RATE_LIMIT_REQUESTS:
        return True
    
    # Record this request
    rate_limit_data[client_ip].append(current_time)
    return False


# =============================================================================
# Authentication
# =============================================================================

def verify_api_key(x_api_key: Optional[str] = Header(None)) -> Optional[str]:
    """
    Verifies API key if authentication is enabled.
    
    If API_KEY environment variable is not set, authentication is disabled.
    """
    if API_KEY is None:
        # Authentication disabled
        return None
    
    if x_api_key is None:
        raise HTTPException(
            status_code=401, 
            detail="Missing API key. Include 'x-api-key' header."
        )
    
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401, 
            detail="Invalid API key"
        )
    
    return x_api_key


# =============================================================================
# Exception Handlers
# =============================================================================

@app.exception_handler(BaseAppError)
async def app_error_handler(request: Request, exc: BaseAppError):
    """Handles custom application errors."""
    logger.error("Application error: %s - %s", exc.__class__.__name__, exc.message)
    return JSONResponse(
        status_code=500,
        content=exc.to_dict()
    )


@app.exception_handler(ScenarioNotFoundError)
async def scenario_error_handler(request: Request, exc: ScenarioNotFoundError):
    """Handles invalid scenario errors."""
    return JSONResponse(
        status_code=400,
        content=exc.to_dict()
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """Handles validation errors."""
    return JSONResponse(
        status_code=422,
        content=exc.to_dict()
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    """Handles unexpected errors."""
    logger.exception("Unexpected error: %s", str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": {}
        }
    )


# =============================================================================
# Middleware
# =============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Logs all requests with timing."""
    start_time = time.time()
    
    response = await call_next(request)
    
    duration_ms = (time.time() - start_time) * 1000
    log_request(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms
    )
    
    return response


# =============================================================================
# Endpoints
# =============================================================================

@app.get("/health")
def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {"status": "ok", "version": APP_VERSION}


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_project(
    request: AnalyzeRequest,
    http_request: Request,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """
    Analyzes project tasks for delay risk.
    
    Returns risk scores, explanations, and recommendations for each task.
    Optionally runs what-if scenario analysis.
    """
    # Check rate limit
    client_ip = http_request.client.host if http_request.client else "unknown"
    if _check_rate_limit(client_ip):
        logger.warning("Rate limit exceeded for IP: %s", client_ip)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds."
        )
    try:
        results = run_analysis(what_if=request.what_if)
        return {"results": results}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Analysis failed: %s", str(e))
        raise HTTPException(status_code=500, detail="Analysis failed")


@app.post("/analyze/refresh", response_model=AnalyzeResponse)
def analyze_project_refresh(
    request: AnalyzeRequest,
    http_request: Request,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """
    Analyzes project with forced model retraining.
    
    Clears the model cache and retrains from scratch.
    Use this after configuration changes or to ensure fresh analysis.
    """
    # Check rate limit
    client_ip = http_request.client.host if http_request.client else "unknown"
    if _check_rate_limit(client_ip):
        logger.warning("Rate limit exceeded for IP: %s", client_ip)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds."
        )
    try:
        clear_model_cache()
        results = run_analysis(what_if=request.what_if, force_retrain=True)
        return {"results": results}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Analysis refresh failed: %s", str(e))
        raise HTTPException(status_code=500, detail="Analysis failed")


@app.delete("/cache")
def clear_cache(api_key: Optional[str] = Depends(verify_api_key)):
    """Clears the model cache."""
    clear_model_cache()
    return {"status": "cache_cleared"}


@app.get("/history")
def get_history(
    limit: int = 20,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """
    Gets the history of recent analyses.
    
    Returns list of analysis summaries with risk counts.
    """
    return {"analyses": get_analysis_history(limit=limit)}


@app.get("/history/{analysis_id}")
def get_analysis_detail(
    analysis_id: int,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """
    Gets a specific analysis by ID with full results.
    """
    result = get_analysis_by_id(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result


@app.get("/stats")
def get_statistics(api_key: Optional[str] = Depends(verify_api_key)):
    """
    Gets aggregate statistics from all analyses.
    
    Returns total analyses, task counts, risk distributions.
    """
    return get_stats()


@app.get("/metrics")
def prometheus_metrics():
    """
    Exposes Prometheus metrics.
    
    Returns metrics in Prometheus text format for scraping.
    """
    from fastapi.responses import Response
    return Response(
        content=get_metrics(),
        media_type=get_content_type()
    )


