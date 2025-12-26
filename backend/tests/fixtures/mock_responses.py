"""
Dynamic mock response generator for testing all scenario combinations.

Generates valid mock Claude responses that vary based on input parameters,
allowing realistic testing without actual API calls.
"""

from typing import Literal, TypedDict

from app.models import (
    CloudPlatform,
    DataClassification,
    IntegrationPattern,
    ScaleTier,
    UseCase,
)


# TypedDict definitions matching Pydantic models for type safety
class ComponentDict(TypedDict):
    """Matches ArchitectureComponent model."""
    name: str
    service: str
    purpose: str
    phiTouchpoint: bool


# DataFlowDict uses functional form because 'from' is a reserved keyword
DataFlowDict = TypedDict("DataFlowDict", {
    "from": str,
    "to": str,
    "data": str,
    "encrypted": bool,
})


class ComplianceItemDict(TypedDict):
    """Matches ComplianceItem model."""
    category: Literal["administrative", "physical", "technical"]
    requirement: str
    implementation: str
    priority: Literal["required", "recommended", "addressable"]


class SampleCodeDict(TypedDict):
    """Matches SampleCode model."""
    python: str
    typescript: str


class ArchitectureDict(TypedDict):
    """Matches Architecture model."""
    mermaidDiagram: str
    components: list[ComponentDict]
    dataFlows: list[DataFlowDict]


class ComplianceDict(TypedDict):
    """Matches Compliance model."""
    checklist: list[ComplianceItemDict]
    baaRequirements: str


class DeploymentDict(TypedDict):
    """Matches Deployment model."""
    steps: list[str]
    iamPolicies: list[str]
    networkConfig: str
    monitoringSetup: str


class ArchitectureResponseDict(TypedDict):
    """Matches ArchitectureResponse model (full response with sampleCode)."""
    architecture: ArchitectureDict
    compliance: ComplianceDict
    deployment: DeploymentDict
    sampleCode: SampleCodeDict


class StreamingResponseDict(TypedDict):
    """Streaming response without sampleCode."""
    architecture: ArchitectureDict
    compliance: ComplianceDict
    deployment: DeploymentDict


class CodeResponseDict(TypedDict):
    """Code generation response."""
    sampleCode: SampleCodeDict


class UseCaseInfo(TypedDict):
    """Use case description info."""
    purpose: str
    data_type: str


class IntegrationInfo(TypedDict):
    """Integration pattern info."""
    pattern_name: str
    description: str


# Cloud-specific service mappings
CLOUD_SERVICES = {
    CloudPlatform.AWS_BEDROCK: {
        "api_gateway": "Amazon API Gateway",
        "ai_service": "Amazon Bedrock (Claude)",
        "storage": "Amazon S3",
        "database": "Amazon DynamoDB",
        "queue": "Amazon SQS",
        "monitoring": "Amazon CloudWatch",
        "kms": "AWS KMS",
        "secrets": "AWS Secrets Manager",
        "iam": "AWS IAM",
        "vpc": "Amazon VPC",
        "lambda": "AWS Lambda",
        "step_functions": "AWS Step Functions",
        "eventbridge": "Amazon EventBridge",
    },
    CloudPlatform.GCP_VERTEX: {
        "api_gateway": "Cloud Endpoints",
        "ai_service": "Vertex AI (Claude)",
        "storage": "Cloud Storage",
        "database": "Cloud Firestore",
        "queue": "Cloud Pub/Sub",
        "monitoring": "Cloud Monitoring",
        "kms": "Cloud KMS",
        "secrets": "Secret Manager",
        "iam": "Cloud IAM",
        "vpc": "VPC Network",
        "lambda": "Cloud Functions",
        "step_functions": "Cloud Workflows",
        "eventbridge": "Eventarc",
    },
}

# Use case specific descriptions
USE_CASE_DESCRIPTIONS = {
    UseCase.CLINICAL_DOCUMENTATION: {
        "purpose": "AI-assisted clinical note generation and summarization",
        "data_type": "clinical notes and patient encounters",
    },
    UseCase.PRIOR_AUTHORIZATION: {
        "purpose": "Streamlined payer-provider authorization workflows",
        "data_type": "authorization requests and medical necessity documentation",
    },
    UseCase.MEDICAL_CODING: {
        "purpose": "ICD-10 and CPT code suggestion and validation",
        "data_type": "clinical documentation for coding analysis",
    },
    UseCase.PATIENT_COMMUNICATION: {
        "purpose": "Secure patient messaging and appointment preparation",
        "data_type": "patient communications and appointment information",
    },
}

# Integration pattern specific configurations
INTEGRATION_CONFIGS = {
    IntegrationPattern.API_GATEWAY: {
        "pattern_name": "Synchronous REST API",
        "description": "Real-time request/response pattern",
    },
    IntegrationPattern.EVENT_DRIVEN: {
        "pattern_name": "Asynchronous Event-Driven",
        "description": "Message queue-based async processing",
    },
    IntegrationPattern.BATCH_PROCESSING: {
        "pattern_name": "Scheduled Batch Processing",
        "description": "Bulk document processing pipeline",
    },
}


def generate_mock_architecture_response(
    use_case: UseCase,
    cloud_platform: CloudPlatform,
    integration_pattern: IntegrationPattern,
    data_classification: DataClassification,
    scale_tier: ScaleTier,
) -> ArchitectureResponseDict:
    """
    Generate a valid mock response that varies based on input parameters.

    This ensures responses are realistic while maintaining fast test execution.
    """
    services = CLOUD_SERVICES[cloud_platform]
    use_case_info = USE_CASE_DESCRIPTIONS[use_case]
    integration_info = INTEGRATION_CONFIGS[integration_pattern]

    # PHI touchpoint based on data classification
    has_phi = data_classification in [DataClassification.PHI, DataClassification.PII]

    # Scale-based component count
    component_counts = {
        ScaleTier.PILOT: 4,
        ScaleTier.PRODUCTION: 6,
        ScaleTier.ENTERPRISE: 8,
    }
    component_count = component_counts[scale_tier]

    # Generate Mermaid diagram
    mermaid_diagram = _generate_mermaid_diagram(
        cloud_platform, integration_pattern, services
    )

    # Generate components based on integration pattern
    components = _generate_components(
        cloud_platform,
        integration_pattern,
        services,
        use_case_info,
        has_phi,
        component_count,
    )

    # Generate data flows
    data_flows = _generate_data_flows(
        cloud_platform, integration_pattern, services, use_case_info
    )

    # Generate compliance checklist
    compliance_checklist = _generate_compliance_checklist(
        cloud_platform, data_classification, services
    )

    # Generate deployment steps
    deployment_steps = _generate_deployment_steps(
        cloud_platform, integration_pattern, scale_tier, services
    )

    # Generate IAM policies
    iam_policies = _generate_iam_policies(cloud_platform, integration_pattern)

    return {
        "architecture": {
            "mermaidDiagram": mermaid_diagram,
            "components": components,
            "dataFlows": data_flows,
        },
        "compliance": {
            "checklist": compliance_checklist,
            "baaRequirements": f"Sign BAA with {'AWS' if cloud_platform == CloudPlatform.AWS_BEDROCK else 'Google Cloud'} before processing PHI",
        },
        "deployment": {
            "steps": deployment_steps,
            "iamPolicies": iam_policies,
            "networkConfig": f"Deploy within {services['vpc']} with private subnets and NAT gateway",
            "monitoringSetup": f"Configure {services['monitoring']} dashboards and alerts for latency, errors, and PHI access",
        },
        "sampleCode": {
            "python": _generate_python_code(cloud_platform, use_case),
            "typescript": _generate_typescript_code(cloud_platform, use_case),
        },
    }


def generate_mock_streaming_response(
    use_case: UseCase,
    cloud_platform: CloudPlatform,
    integration_pattern: IntegrationPattern,
    data_classification: DataClassification,
    scale_tier: ScaleTier,
) -> StreamingResponseDict:
    """
    Generate mock response for streaming endpoint (no sampleCode).
    """
    full_response = generate_mock_architecture_response(
        use_case, cloud_platform, integration_pattern, data_classification, scale_tier
    )
    # Return streaming response without sampleCode
    return StreamingResponseDict(
        architecture=full_response["architecture"],
        compliance=full_response["compliance"],
        deployment=full_response["deployment"],
    )


def generate_mock_code_response(
    use_case: UseCase,
    cloud_platform: CloudPlatform,
) -> CodeResponseDict:
    """Generate mock response for code generation endpoint."""
    return CodeResponseDict(
        sampleCode=SampleCodeDict(
            python=_generate_python_code(cloud_platform, use_case),
            typescript=_generate_typescript_code(cloud_platform, use_case),
        )
    )


def _generate_mermaid_diagram(
    cloud_platform: CloudPlatform,
    integration_pattern: IntegrationPattern,
    services: dict[str, str],
) -> str:
    """Generate a valid Mermaid flowchart diagram."""
    if integration_pattern == IntegrationPattern.API_GATEWAY:
        return f"""flowchart TD
    client[Client Application] --> apigw[{services['api_gateway']}]
    apigw --> auth[Authentication Service]
    auth --> lambda[{services['lambda']}]
    lambda --> ai[{services['ai_service']}]
    ai --> lambda
    lambda --> db[({services['database']})]
    lambda --> apigw
    apigw --> client"""

    elif integration_pattern == IntegrationPattern.EVENT_DRIVEN:
        return f"""flowchart TD
    producer[Event Producer] --> queue[{services['queue']}]
    queue --> processor[{services['lambda']}]
    processor --> ai[{services['ai_service']}]
    ai --> processor
    processor --> storage[({services['storage']})]
    processor --> notify[{services['eventbridge']}]
    notify --> consumer[Event Consumer]"""

    else:  # BATCH_PROCESSING
        return f"""flowchart TD
    source[({services['storage']})] --> trigger[{services['eventbridge']}]
    trigger --> workflow[{services['step_functions']}]
    workflow --> process[{services['lambda']}]
    process --> ai[{services['ai_service']}]
    ai --> process
    process --> output[({services['storage']})]
    workflow --> monitor[{services['monitoring']}]"""


def _generate_components(
    cloud_platform: CloudPlatform,
    integration_pattern: IntegrationPattern,
    services: dict[str, str],
    use_case_info: UseCaseInfo,
    has_phi: bool,
    component_count: int,
) -> list[ComponentDict]:
    """Generate architecture components based on pattern."""
    base_components = [
        {
            "name": "API Gateway",
            "service": services["api_gateway"],
            "purpose": f"Entry point for {use_case_info['purpose']}",
            "phiTouchpoint": False,
        },
        {
            "name": "AI Processing",
            "service": services["ai_service"],
            "purpose": f"Process {use_case_info['data_type']} using Claude",
            "phiTouchpoint": has_phi,
        },
        {
            "name": "Data Storage",
            "service": services["storage"],
            "purpose": f"Store {use_case_info['data_type']}",
            "phiTouchpoint": has_phi,
        },
        {
            "name": "Secrets Management",
            "service": services["secrets"],
            "purpose": "Secure storage for API keys and credentials",
            "phiTouchpoint": False,
        },
    ]

    # Add pattern-specific components
    if integration_pattern == IntegrationPattern.EVENT_DRIVEN:
        base_components.append(
            {
                "name": "Message Queue",
                "service": services["queue"],
                "purpose": "Async message processing",
                "phiTouchpoint": has_phi,
            }
        )
    elif integration_pattern == IntegrationPattern.BATCH_PROCESSING:
        base_components.append(
            {
                "name": "Workflow Orchestration",
                "service": services["step_functions"],
                "purpose": "Coordinate batch processing steps",
                "phiTouchpoint": False,
            }
        )

    # Add monitoring component
    base_components.append(
        {
            "name": "Monitoring",
            "service": services["monitoring"],
            "purpose": "Track performance and compliance metrics",
            "phiTouchpoint": False,
        }
    )

    return base_components[:component_count]


def _generate_data_flows(
    cloud_platform: CloudPlatform,
    integration_pattern: IntegrationPattern,
    services: dict[str, str],
    use_case_info: UseCaseInfo,
) -> list[DataFlowDict]:
    """Generate data flow definitions."""
    return [
        {
            "from": "Client",
            "to": services["api_gateway"],
            "data": f"Incoming {use_case_info['data_type']}",
            "encrypted": True,
        },
        {
            "from": services["api_gateway"],
            "to": services["lambda"],
            "data": "Validated request payload",
            "encrypted": True,
        },
        {
            "from": services["lambda"],
            "to": services["ai_service"],
            "data": "Processed prompt with context",
            "encrypted": True,
        },
        {
            "from": services["ai_service"],
            "to": services["lambda"],
            "data": "AI-generated response",
            "encrypted": True,
        },
        {
            "from": services["lambda"],
            "to": services["storage"],
            "data": "Audit logs and processed results",
            "encrypted": True,
        },
    ]


def _generate_compliance_checklist(
    cloud_platform: CloudPlatform,
    data_classification: DataClassification,
    services: dict[str, str],
) -> list[ComplianceItemDict]:
    """Generate HIPAA compliance checklist items."""
    items = [
        {
            "category": "technical",
            "requirement": "Encryption at rest",
            "implementation": f"Enable {services['kms']} encryption for all data stores",
            "priority": "required",
        },
        {
            "category": "technical",
            "requirement": "Encryption in transit",
            "implementation": "TLS 1.2+ for all API communications",
            "priority": "required",
        },
        {
            "category": "technical",
            "requirement": "Access controls",
            "implementation": f"Implement least-privilege {services['iam']} policies",
            "priority": "required",
        },
        {
            "category": "administrative",
            "requirement": "Audit logging",
            "implementation": f"Enable {services['monitoring']} with log retention",
            "priority": "required",
        },
        {
            "category": "administrative",
            "requirement": "BAA execution",
            "implementation": f"Sign BAA with {'AWS' if cloud_platform == CloudPlatform.AWS_BEDROCK else 'Google Cloud'}",
            "priority": "required",
        },
        {
            "category": "physical",
            "requirement": "Data residency",
            "implementation": "Deploy in US regions with HIPAA eligibility",
            "priority": "required",
        },
    ]

    if data_classification == DataClassification.PHI:
        items.append(
            {
                "category": "technical",
                "requirement": "PHI access monitoring",
                "implementation": "Real-time alerts for PHI access patterns",
                "priority": "required",
            }
        )

    return items


def _generate_deployment_steps(
    cloud_platform: CloudPlatform,
    integration_pattern: IntegrationPattern,
    scale_tier: ScaleTier,
    services: dict[str, str],
) -> list[str]:
    """Generate deployment steps."""
    steps = [
        f"1. Configure {services['vpc']} with private subnets",
        f"2. Set up {services['kms']} for encryption",
        f"3. Create {services['secrets']} entries for API keys",
        f"4. Deploy {services['api_gateway']} with authentication",
        f"5. Configure {services['lambda']} with VPC access",
        f"6. Set up {services['ai_service']} integration",
        f"7. Enable {services['monitoring']} dashboards and alerts",
    ]

    if scale_tier == ScaleTier.ENTERPRISE:
        steps.extend(
            [
                "8. Configure multi-region failover",
                "9. Set up disaster recovery procedures",
                "10. Implement rate limiting and throttling",
            ]
        )

    return steps


def _generate_iam_policies(
    cloud_platform: CloudPlatform,
    integration_pattern: IntegrationPattern,
) -> list[str]:
    """Generate IAM policy definitions as JSON strings."""
    if cloud_platform == CloudPlatform.AWS_BEDROCK:
        return [
            '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["bedrock:InvokeModel"],"Resource":"arn:aws:bedrock:*:*:model/anthropic.*"}]}',
            '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["secretsmanager:GetSecretValue"],"Resource":"arn:aws:secretsmanager:*:*:secret:gsi/*"}]}',
            '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["logs:CreateLogGroup","logs:CreateLogStream","logs:PutLogEvents"],"Resource":"*"}]}',
        ]
    else:
        return [
            '{"bindings":[{"role":"roles/aiplatform.user","members":["serviceAccount:gsi-service@project.iam.gserviceaccount.com"]}]}',
            '{"bindings":[{"role":"roles/secretmanager.secretAccessor","members":["serviceAccount:gsi-service@project.iam.gserviceaccount.com"]}]}',
            '{"bindings":[{"role":"roles/logging.logWriter","members":["serviceAccount:gsi-service@project.iam.gserviceaccount.com"]}]}',
        ]


def _generate_python_code(cloud_platform: CloudPlatform, use_case: UseCase) -> str:
    """Generate sample Python code."""
    use_case_label = use_case.value.replace("-", " ").title()

    if cloud_platform == CloudPlatform.AWS_BEDROCK:
        return f'''"""
Sample Python code for {use_case_label} using AWS Bedrock.
"""

import json
import boto3
from botocore.config import Config

# Configure Bedrock client
bedrock = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1",
    config=Config(retries={{"max_attempts": 3}})
)

def invoke_claude(prompt: str) -> str:
    """Invoke Claude on Bedrock for {use_case_label}."""
    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps({{
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [
                {{"role": "user", "content": prompt}}
            ]
        }})
    )
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]
'''
    else:
        return f'''"""
Sample Python code for {use_case_label} using GCP Vertex AI.
"""

import vertexai
from vertexai.generative_models import GenerativeModel

# Initialize Vertex AI
vertexai.init(project="your-project-id", location="us-central1")

def invoke_claude(prompt: str) -> str:
    """Invoke Claude on Vertex AI for {use_case_label}."""
    model = GenerativeModel("claude-3-sonnet@20240229")
    response = model.generate_content(
        prompt,
        generation_config={{
            "max_output_tokens": 4096,
            "temperature": 0.7,
        }}
    )
    return response.text
'''


def _generate_typescript_code(cloud_platform: CloudPlatform, use_case: UseCase) -> str:
    """Generate sample TypeScript code."""
    use_case_label = use_case.value.replace("-", " ").title()

    if cloud_platform == CloudPlatform.AWS_BEDROCK:
        return f'''/**
 * Sample TypeScript code for {use_case_label} using AWS Bedrock.
 */

import {{ BedrockRuntimeClient, InvokeModelCommand }} from "@aws-sdk/client-bedrock-runtime";

const client = new BedrockRuntimeClient({{ region: "us-east-1" }});

export async function invokeClaude(prompt: string): Promise<string> {{
  const command = new InvokeModelCommand({{
    modelId: "anthropic.claude-3-sonnet-20240229-v1:0",
    contentType: "application/json",
    accept: "application/json",
    body: JSON.stringify({{
      anthropic_version: "bedrock-2023-05-31",
      max_tokens: 4096,
      messages: [{{ role: "user", content: prompt }}]
    }})
  }});

  const response = await client.send(command);
  const result = JSON.parse(new TextDecoder().decode(response.body));
  return result.content[0].text;
}}
'''
    else:
        return f'''/**
 * Sample TypeScript code for {use_case_label} using GCP Vertex AI.
 */

import {{ VertexAI }} from "@google-cloud/vertexai";

const vertexAI = new VertexAI({{
  project: "your-project-id",
  location: "us-central1"
}});

export async function invokeClaude(prompt: string): Promise<string> {{
  const model = vertexAI.getGenerativeModel({{
    model: "claude-3-sonnet@20240229"
  }});

  const result = await model.generateContent({{
    contents: [{{ role: "user", parts: [{{ text: prompt }}] }}],
    generationConfig: {{
      maxOutputTokens: 4096,
      temperature: 0.7
    }}
  }});

  return result.response.candidates[0].content.parts[0].text;
}}
'''
