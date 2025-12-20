"""
GSI Reference Architecture Generator - FastAPI Application

This API generates healthcare-specific Claude deployment architectures
for Global System Integrator (GSI) partners.
"""

import os
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import ArchitectureRequest, ArchitectureResponse
from app.services.generator import ArchitectureGenerator

# Load environment variables
load_dotenv()

# Initialize the generator (will be set up in lifespan)
generator: Optional[ArchitectureGenerator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup application resources."""
    global generator
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY environment variable is required")
    
    generator = ArchitectureGenerator(api_key)
    yield
    # Cleanup if needed
    generator = None


# Create FastAPI app
app = FastAPI(
    title="GSI Reference Architecture Generator",
    description="Generate healthcare-specific Claude deployment architectures for GSI partners",
    version="1.0.0",
    lifespan=lifespan,
)

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
async def generate_architecture(request: ArchitectureRequest):
    """
    Generate a reference architecture based on the provided configuration.
    
    This endpoint uses Claude to generate:
    - Architecture diagram (Mermaid format)
    - Component details with PHI touchpoints
    - HIPAA compliance checklist
    - Cloud-specific deployment guide
    - Sample integration code
    """
    if generator is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        response = await generator.generate(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the error in production
        print(f"Generation error: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to generate architecture. Please try again."
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
