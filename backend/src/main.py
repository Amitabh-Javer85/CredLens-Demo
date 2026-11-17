import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.core.logging import logger
from src.api.applications import router as applications_router

app = FastAPI(
    title="CredLens API",
    description="Local synthetic-only portfolio demo. Select a fixture at GET /v1/applications/samples, POST its applicant_id, then poll status and fetch the memo. MOCK integrations; ILLUSTRATIVE calculations; no authentication or compliance certification. Jobs expire after 24 hours.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logger middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID", "unknown")
    logger.info(f"Incoming request: {request.method} {request.url.path}", extra={"request_id": request_id})
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        logger.info(
            f"Completed request: {request.method} {request.url.path} with status {response.status_code}",
            extra={"request_id": request_id, "duration_ms": int(duration * 1000)}
        )
        return response
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url.path} - Error: {str(e)}",
            extra={"request_id": request_id, "duration_ms": int(duration * 1000)},
            exc_info=True
        )
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred. Please try again later."
                }
            }
        )

# Register routers
app.include_router(applications_router, prefix="/v1/applications", tags=["Applications"])

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "success": True,
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }
