"""
Pydantic models for API request/response validation.
"""

from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field


# Request enums
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


# Request model
class ArchitectureRequest(BaseModel):
    """Request body for architecture generation."""
    
    use_case: UseCase = Field(alias="useCase")
    cloud_platform: CloudPlatform = Field(alias="cloudPlatform")
    integration_pattern: IntegrationPattern = Field(alias="integrationPattern")
    data_classification: DataClassification = Field(alias="dataClassification")
    scale_tier: ScaleTier = Field(alias="scaleTier")

    class Config:
        populate_by_name = True


# Response models
class ArchitectureComponent(BaseModel):
    """A component in the architecture."""
    
    name: str
    service: str
    purpose: str
    phi_touchpoint: bool = Field(alias="phiTouchpoint")

    class Config:
        populate_by_name = True


class DataFlow(BaseModel):
    """A data flow between components."""
    
    from_component: str = Field(alias="from")
    to_component: str = Field(alias="to")
    data: str
    encrypted: bool

    class Config:
        populate_by_name = True


class ComplianceItem(BaseModel):
    """A HIPAA compliance checklist item."""
    
    category: Literal["administrative", "physical", "technical"]
    requirement: str
    implementation: str
    priority: Literal["required", "recommended", "addressable"]


class Architecture(BaseModel):
    """Generated architecture details."""
    
    mermaid_diagram: str = Field(alias="mermaidDiagram")
    components: list[ArchitectureComponent]
    data_flows: list[DataFlow] = Field(alias="dataFlows")

    class Config:
        populate_by_name = True


class Compliance(BaseModel):
    """HIPAA compliance information."""
    
    checklist: list[ComplianceItem]
    baa_requirements: str = Field(alias="baaRequirements")

    class Config:
        populate_by_name = True


class Deployment(BaseModel):
    """Deployment configuration details."""
    
    steps: list[str]
    iam_policies: list[str] = Field(alias="iamPolicies")
    network_config: str = Field(alias="networkConfig")
    monitoring_setup: str = Field(alias="monitoringSetup")

    class Config:
        populate_by_name = True


class SampleCode(BaseModel):
    """Sample integration code."""
    
    python: str
    typescript: str


class ArchitectureResponse(BaseModel):
    """Complete response with generated architecture."""

    architecture: Architecture
    compliance: Compliance
    deployment: Deployment
    sample_code: SampleCode = Field(alias="sampleCode")

    class Config:
        populate_by_name = True
        by_alias = True


# Code generation models
class CodeGenerationRequest(BaseModel):
    """Request body for code generation."""

    use_case: UseCase = Field(alias="useCase")
    cloud_platform: CloudPlatform = Field(alias="cloudPlatform")
    architecture_summary: str = Field(alias="architectureSummary")

    class Config:
        populate_by_name = True


class CodeGenerationResponse(BaseModel):
    """Response with generated sample code."""

    sample_code: SampleCode = Field(alias="sampleCode")

    class Config:
        populate_by_name = True
        by_alias = True
