"""
Reference Architecture Generator - Vercel Serverless Entry Point
All code in single file for Vercel compatibility.
"""

import json
import logging
import os
import time
import uuid
from collections import defaultdict
from enum import Enum
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import anthropic

# Configure logging with structured format for audit trail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Simple in-memory rate limiter for serverless (resets on cold start)
# For production, consider Upstash Redis or Vercel KV
class SimpleRateLimiter:
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        minute_ago = now - 60

        # Clean old requests
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip] if ts > minute_ago
        ]

        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return False

        self.requests[client_ip].append(now)
        return True

rate_limiter = SimpleRateLimiter(requests_per_minute=10)

# Constants
MAX_RESPONSE_SIZE = 500_000  # 500KB limit for Claude responses


# ============= MODELS =============

class UseCase(str, Enum):
    CLINICAL_DOCUMENTATION = "clinical-documentation"
    PRIOR_AUTHORIZATION = "prior-authorization"
    MEDICAL_CODING = "medical-coding"
    PATIENT_COMMUNICATION = "patient-communication"


class CloudPlatform(str, Enum):
    AWS_BEDROCK = "aws-bedrock"
    GCP_VERTEX = "gcp-vertex"


class IntegrationPattern(str, Enum):
    API_GATEWAY = "api-gateway"
    EVENT_DRIVEN = "event-driven"
    BATCH_PROCESSING = "batch-processing"


class DataClassification(str, Enum):
    PHI = "phi"
    PII = "pii"
    DE_IDENTIFIED = "de-identified"
    PUBLIC = "public"


class ScaleTier(str, Enum):
    PILOT = "pilot"
    PRODUCTION = "production"
    ENTERPRISE = "enterprise"


class ArchitectureRequest(BaseModel):
    use_case: UseCase = Field(alias="useCase")
    cloud_platform: CloudPlatform = Field(alias="cloudPlatform")
    integration_pattern: IntegrationPattern = Field(alias="integrationPattern")
    data_classification: DataClassification = Field(alias="dataClassification")
    scale_tier: ScaleTier = Field(alias="scaleTier")

    class Config:
        populate_by_name = True


class ArchitectureComponent(BaseModel):
    name: str
    service: str
    purpose: str
    phi_touchpoint: bool = Field(alias="phiTouchpoint")

    class Config:
        populate_by_name = True


class DataFlow(BaseModel):
    from_component: str = Field(alias="from")
    to_component: str = Field(alias="to")
    data: str
    encrypted: bool

    class Config:
        populate_by_name = True


class ComplianceItem(BaseModel):
    category: Literal["administrative", "physical", "technical"]
    requirement: str
    implementation: str
    priority: Literal["required", "recommended"]


class Architecture(BaseModel):
    mermaid_diagram: str = Field(alias="mermaidDiagram")
    components: list[ArchitectureComponent]
    data_flows: list[DataFlow] = Field(alias="dataFlows")

    class Config:
        populate_by_name = True


class Compliance(BaseModel):
    checklist: list[ComplianceItem]
    baa_requirements: str = Field(alias="baaRequirements")

    class Config:
        populate_by_name = True


class Deployment(BaseModel):
    steps: list[str]
    iam_policies: list[str] = Field(alias="iamPolicies")
    network_config: str = Field(alias="networkConfig")
    monitoring_setup: str = Field(alias="monitoringSetup")

    class Config:
        populate_by_name = True


class SampleCode(BaseModel):
    python: str
    typescript: str


class ArchitectureResponse(BaseModel):
    architecture: Architecture
    compliance: Compliance
    deployment: Deployment
    sample_code: SampleCode = Field(alias="sampleCode")

    class Config:
        populate_by_name = True
        by_alias = True


# ============= PROMPTS =============

SYSTEM_PROMPT = """You are an expert Healthcare IT Solutions Architect. Generate complete reference architectures with Mermaid diagrams, components, compliance checklists, deployment steps, and sample code in JSON format."""


# ============= GENERATOR =============

class ArchitectureGenerator:
    def __init__(self, api_key: str):
        # Add timeout to prevent hanging requests (120 seconds)
        self.client = anthropic.Anthropic(api_key=api_key, timeout=120.0)
        # Model configurable via env var with sensible default
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    async def generate(self, request: ArchitectureRequest) -> ArchitectureResponse:
        user_prompt = f"""Generate a complete healthcare reference architecture for:
- Use Case: {request.use_case.value}
- Cloud Platform: {request.cloud_platform.value}
- Integration Pattern: {request.integration_pattern.value}
- Data Classification: {request.data_classification.value}
- Scale Tier: {request.scale_tier.value}

Return valid JSON with this structure:
{{
  "architecture": {{
    "mermaidDiagram": "flowchart TD...",
    "components": [{{"name": "", "service": "", "purpose": "", "phiTouchpoint": true}}],
    "dataFlows": [{{"from": "", "to": "", "data": "", "encrypted": true}}]
  }},
  "compliance": {{
    "checklist": [{{"category": "technical", "requirement": "", "implementation": "", "priority": "required"}}],
    "baaRequirements": ""
  }},
  "deployment": {{
    "steps": [],
    "iamPolicies": [],
    "networkConfig": "",
    "monitoringSetup": ""
  }},
  "sampleCode": {{
    "python": "",
    "typescript": ""
  }}
}}

Return ONLY the JSON, no markdown or explanation."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=8192,  # Reduced from 16384 to control costs
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        # Check for truncation
        if message.stop_reason == "max_tokens":
            logger.warning("Response was truncated due to max_tokens limit")
            raise ValueError("Response exceeded maximum length. Please try a simpler configuration.")

        response_text = message.content[0].text.strip()

        # Validate response size
        if len(response_text) > MAX_RESPONSE_SIZE:
            logger.error(f"Response too large: {len(response_text)} bytes")
            raise ValueError("Response too large")

        # Clean markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
        if response_text.endswith("```"):
            response_text = response_text.rsplit("```", 1)[0]
        response_text = response_text.strip()

        # Parse and validate JSON
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            raise ValueError(f"Invalid response format from AI model")

        # Validate required keys exist
        required_keys = ["architecture", "compliance", "deployment", "sampleCode"]
        if not all(key in data for key in required_keys):
            missing = [k for k in required_keys if k not in data]
            logger.error(f"Missing required keys in response: {missing}")
            raise ValueError("Incomplete response from AI model")

        return ArchitectureResponse.model_validate(data)


# ============= APP =============

app = FastAPI(title="Reference Architecture Generator")

# Configure CORS from environment variable (comma-separated origins)
# Defaults to common development/production origins
cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:5173,https://claude-gsi.vercel.app")
cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

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

_generator = None


def get_generator() -> ArchitectureGenerator:
    global _generator
    if _generator is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        # Validate API key format
        if not api_key.startswith("sk-ant-"):
            raise RuntimeError("ANTHROPIC_API_KEY appears invalid")
        _generator = ArchitectureGenerator(api_key)
    return _generator


@app.get("/api")
@app.get("/api/")
@app.get("/api/health")
async def health_check():
    """Health check endpoint - does not expose sensitive information."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    return {
        "status": "healthy",
        "service": "gsi-architecture-generator",
        "api_key_configured": bool(api_key and len(api_key) > 10)
    }


@app.post("/api/generate-architecture", response_model=ArchitectureResponse)
async def generate_architecture(request: ArchitectureRequest, http_request: Request):
    """Generate a healthcare reference architecture using Claude."""
    # Rate limiting check
    client_ip = http_request.client.host if http_request.client else "unknown"
    if not rate_limiter.is_allowed(client_ip):
        logger.warning(f"Rate limit exceeded for {client_ip}")
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please wait before making another request."
        )

    try:
        generator = get_generator()
        response = await generator.generate(request)
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
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
