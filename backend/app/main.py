"""
Reference Architecture Generator - FastAPI Application

This API generates healthcare-specific Claude deployment architectures.
"""

import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import anthropic

from app.models import ArchitectureRequest, ArchitectureResponse
from app.services.generator import ArchitectureGenerator

# Configure logging with structured format for audit trail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize the generator (will be set up in lifespan)
generator: Optional[ArchitectureGenerator] = None


def validate_api_key(api_key: str) -> None:
    """Validate the Anthropic API key format."""
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY environment variable is required")
    if not api_key.startswith("sk-ant-"):
        raise RuntimeError("ANTHROPIC_API_KEY appears invalid (must start with 'sk-ant-')")
    if len(api_key) < 50:
        raise RuntimeError("ANTHROPIC_API_KEY appears invalid (too short)")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup application resources."""
    global generator

    api_key = os.getenv("ANTHROPIC_API_KEY")
    validate_api_key(api_key)
    logger.info("API key validated successfully")

    generator = ArchitectureGenerator(api_key)
    logger.info("Architecture generator initialized")
    yield
    # Cleanup if needed
    generator = None
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Reference Architecture Generator",
    description="Generate healthcare-specific Claude deployment architectures",
    version="1.0.0",
    lifespan=lifespan,
)

# Add rate limiter to app state and register error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS with security check
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

# Security: Prevent wildcard with credentials (CORS vulnerability)
has_wildcard = "*" in cors_origins
if has_wildcard:
    logger.warning("CORS wildcard detected - disabling credentials for security")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=not has_wildcard,  # Disable credentials if wildcard present
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # HTTPS enforcement
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    # Content Security Policy
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


# Audit logging middleware
@app.middleware("http")
async def audit_log(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Log request
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"[{request_id}] Request: {request.method} {request.url.path} from {client_ip}")

    response = await call_next(request)

    # Log response
    duration_ms = (time.time() - start_time) * 1000
    logger.info(f"[{request_id}] Response: {response.status_code} in {duration_ms:.2f}ms")

    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "gsi-architecture-generator"}


@app.post("/api/generate-architecture", response_model=ArchitectureResponse)
@limiter.limit("10/minute")  # Rate limit: 10 requests per minute per IP
async def generate_architecture(request: Request, arch_request: ArchitectureRequest):
    """
    Generate a reference architecture based on the provided configuration.

    This endpoint uses Claude to generate:
    - Architecture diagram (Mermaid format)
    - Component details with PHI touchpoints
    - HIPAA compliance checklist
    - Cloud-specific deployment guide
    - Sample integration code

    Rate limited to 10 requests per minute per IP address.
    """
    if generator is None:
        logger.error("Generator not initialized when handling request")
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        logger.info(f"Generating architecture for use_case={arch_request.use_case}, platform={arch_request.cloud_platform}")
        response = await generator.generate(arch_request)
        logger.info("Architecture generation completed successfully")
        return response
    except ValueError as e:
        # Sanitize validation errors - only show safe messages
        error_msg = str(e)
        safe_messages = [
            "Response exceeded maximum length",
            "Response too large",
            "Invalid response format from AI model",
            "Incomplete response from AI model",
        ]
        if not any(msg in error_msg for msg in safe_messages):
            error_msg = "Invalid request parameters"
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=error_msg)
    except anthropic.APIConnectionError:
        logger.error("API Connection Error")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable.")
    except anthropic.AuthenticationError:
        logger.error("Authentication Error - check API key configuration")
        raise HTTPException(status_code=500, detail="Service configuration error.")
    except anthropic.RateLimitError:
        logger.warning("Anthropic rate limit exceeded")
        raise HTTPException(status_code=429, detail="Service busy. Please try again later.")
    except anthropic.APIStatusError as e:
        logger.error(f"API Status Error: {e.status_code}")
        raise HTTPException(status_code=500, detail="Failed to generate architecture.")
    except Exception:
        logger.exception("Unexpected error during generation")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate architecture. Please try again."
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
