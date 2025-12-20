"""
GSI Reference Architecture Generator - FastAPI Application

This API generates healthcare-specific Claude deployment architectures
for Global System Integrator (GSI) partners.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.models import ArchitectureRequest, ArchitectureResponse
from app.services.generator import ArchitectureGenerator

# Configure logging
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
    title="GSI Reference Architecture Generator",
    description="Generate healthcare-specific Claude deployment architectures for GSI partners",
    version="1.0.0",
    lifespan=lifespan,
)

# Add rate limiter to app state and register error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate architecture. Please try again."
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
