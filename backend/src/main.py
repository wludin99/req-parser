"""
Government Tender Extraction System - FastAPI Backend
Main application entry point with API routes and middleware.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import os
import logging
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up comprehensive logging
from .utils.logging_config import setup_application_logging, get_logger, get_performance_logger, get_error_tracker

logger, performance_logger, error_tracker = setup_application_logging(
    log_level="INFO",
    log_format="detailed",
    log_file="logs/tender_extraction.log",
    enable_console=True
)

# Initialize FastAPI app
app = FastAPI(
    title="Government Tender Extraction API",
    description="API for extracting structured data from government tender documents",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses with comprehensive monitoring."""
    # Start performance monitoring
    performance_logger.start_timer(f"request_{request.method}_{request.url.path}")
    
    # Log request with detailed information
    logger.info(
        f"Request: {request.method} {request.url}",
        extra={
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "content_type": request.headers.get("content-type"),
            "content_length": request.headers.get("content-length")
        }
    )
    
    try:
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Log response with performance data
        duration = performance_logger.end_timer(
            f"request_{request.method}_{request.url.path}",
            extra_data={
                "status_code": response.status_code,
                "response_size": response.headers.get("content-length")
            }
        )
        
        logger.info(
            f"Response: {response.status_code} - {duration:.4f}s",
            extra={
                "status_code": response.status_code,
                "duration": duration,
                "response_size": response.headers.get("content-length")
            }
        )
        
        return response
        
    except Exception as e:
        # Track error and log with performance data
        error_tracker.track_error(e, {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path
        })
        
        duration = performance_logger.end_timer(
            f"request_{request.method}_{request.url.path}",
            extra_data={"error": str(e)}
        )
        
        logger.error(
            f"Request failed: {request.method} {request.url} - {duration:.4f}s",
            extra={
                "method": request.method,
                "url": str(request.url),
                "duration": duration,
                "error": str(e)
            },
            exc_info=True
        )
        
        raise

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions with comprehensive error tracking."""
    # Track the error with context
    error_tracker.track_error(exc, {
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent")
    })
    
    # Log the error with detailed information
    logger.error(
        f"Unhandled exception: {exc}",
        extra={
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "client_ip": request.client.host if request.client else None,
            "error_type": type(exc).__name__,
            "error_message": str(exc)
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "details": "An unexpected error occurred",
            "timestamp": time.time(),
            "error_id": f"error_{int(time.time())}"
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "tender-extraction-api"}

# Monitoring endpoint
@app.get("/monitoring/status")
async def monitoring_status():
    """Comprehensive monitoring status endpoint."""
    try:
        error_summary = error_tracker.get_error_summary()
        
        return {
            "status": "healthy",
            "service": "tender-extraction-api",
            "timestamp": time.time(),
            "monitoring": {
                "errors": error_summary,
                "performance_logging": performance_logger is not None,
                "error_tracking": error_tracker is not None
            }
        }
    except Exception as e:
        logger.error(f"Error in monitoring status: {e}", exc_info=True)
        return {
            "status": "degraded",
            "service": "tender-extraction-api",
            "timestamp": time.time(),
            "error": "Monitoring data unavailable"
        }

# Import and include API routes
from .api.routes import router
from .models.database import create_tables

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    create_tables()

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
