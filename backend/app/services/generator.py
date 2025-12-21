"""
Architecture Generator Service

Integrates with Claude API to generate healthcare reference architectures.
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import AsyncGenerator, Optional

import anthropic

from app.models import (
    ArchitectureRequest,
    ArchitectureResponse,
    CodeGenerationRequest,
    CodeGenerationResponse,
    UseCase,
    CloudPlatform,
)

logger = logging.getLogger(__name__)

# Constants
MAX_RESPONSE_SIZE = 500_000  # 500KB limit for Claude responses


class ArchitectureGenerator:
    """Generates healthcare reference architectures using Claude."""

    def __init__(self, api_key: str):
        # Add timeout to prevent hanging requests (120 seconds)
        self.client = anthropic.Anthropic(api_key=api_key, timeout=120.0)
        # Model configurable via env var with sensible default
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        self.prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        self.templates_dir = Path(__file__).parent.parent.parent / "templates"
        
        # Load prompts
        self.system_prompt = self._load_prompt("system_prompt.txt")
        self.healthcare_context = self._load_prompt("healthcare_context.txt")
        self.aws_context = self._load_prompt("aws_bedrock_context.txt")
        self.gcp_context = self._load_prompt("gcp_vertex_context.txt")
        self.example_output = self._load_template("example_output.md")

    def _load_prompt(self, filename: str) -> str:
        """Load a prompt file."""
        path = self.prompts_dir / filename
        if path.exists():
            return path.read_text()
        return ""

    def _load_template(self, filename: str) -> str:
        """Load a template file."""
        path = self.templates_dir / filename
        if path.exists():
            return path.read_text()
        return ""

    def _get_use_case_context(self, use_case: UseCase) -> str:
        """Get specific context for the use case."""
        contexts = {
            UseCase.CLINICAL_DOCUMENTATION: """
## Use Case: Clinical Documentation Assistance

### Integration Points
- EHR Systems: Epic, Cerner, Meditech via FHIR R4 APIs
- Dictation Services: Dragon Medical, M*Modal
- Document Storage: FHIR DocumentReference resources

### PHI Considerations
- Patient names, MRNs, dates of birth
- Clinical notes, diagnoses, procedures
- Medication lists, allergies, vitals
- Provider notes and attestations

### Specific Compliance Requirements
- Minimum necessary principle: Only access required clinical data
- Clinical documentation integrity: Prevent unauthorized modifications
- Audit trail: Complete record of all AI-assisted documentation
- Clinician review: All AI-generated content requires human review before filing
- Consent: May require patient notification of AI assistance
""",
            UseCase.PRIOR_AUTHORIZATION: """
## Use Case: Prior Authorization Automation

### Integration Points
- Payer Portals: Direct API or screen scraping alternatives
- Clearinghouses: Change Healthcare, Availity
- X12 EDI: 278 (authorization request/response), 275 (attachments)
- EHR Systems: Order entry, clinical documentation

### PHI Considerations
- Patient demographics and insurance information
- Diagnosis codes (ICD-10) and procedure codes (CPT)
- Clinical documentation supporting medical necessity
- Treatment plans and provider attestations

### Specific Compliance Requirements
- HIPAA Transaction Rule: X12 format compliance
- CMS Interoperability Rules: Electronic prior auth requirements
- Timely response: Regulatory requirements for response times
- Decision transparency: Clear rationale for approvals/denials
""",
            UseCase.MEDICAL_CODING: """
## Use Case: Medical Coding Support

### Integration Points
- Coding Workbenches: 3M, Optum EncoderPro
- CDI Platforms: Clinical documentation improvement tools
- EHR Systems: Clinical documentation access
- Billing Systems: Charge capture, claim submission

### PHI Considerations
- Clinical documentation (operative notes, discharge summaries)
- Procedure notes and findings
- Diagnosis documentation
- Provider queries and clarifications

### Specific Compliance Requirements
- Code accuracy: AI suggestions must be validated by certified coders
- Audit trail: Complete record of suggested vs. selected codes
- Upcoding prevention: Guard against inappropriate code selection
- DRG optimization: Ensure accurate, not inflated, reimbursement
""",
            UseCase.PATIENT_COMMUNICATION: """
## Use Case: Patient Communication

### Integration Points
- Patient Portals: Epic MyChart, Cerner Patient Portal
- Secure Messaging: Encrypted email/SMS platforms
- Scheduling Systems: Appointment management
- Care Management: Care plan tracking, follow-up workflows

### PHI Considerations
- Appointment details and reminders
- Care instructions and medication information
- Test results and next steps
- General health information and education

### Specific Compliance Requirements
- Patient consent: Explicit opt-in for electronic communication
- Identity verification: Confirm patient identity before sharing PHI
- Secure transmission: TLS 1.2+ for all communications
- Opt-out capability: Easy mechanism to stop communications
- Right channel: Route sensitive information appropriately
""",
        }
        return contexts.get(use_case, "")

    def _get_cloud_context(self, platform: CloudPlatform) -> str:
        """Get cloud-specific context."""
        if platform == CloudPlatform.AWS_BEDROCK:
            return self.aws_context
        return self.gcp_context

    def _build_user_prompt(self, request: ArchitectureRequest) -> str:
        """Build the user prompt for Claude."""
        use_case_context = self._get_use_case_context(request.use_case)
        cloud_context = self._get_cloud_context(request.cloud_platform)

        return f"""Generate a complete reference architecture for the following configuration:

## Configuration
- **Use Case**: {request.use_case.value}
- **Cloud Platform**: {request.cloud_platform.value}
- **Integration Pattern**: {request.integration_pattern.value}
- **Data Classification**: {request.data_classification.value}
- **Scale Tier**: {request.scale_tier.value}

## Healthcare Context
{self.healthcare_context}

{use_case_context}

## Cloud Platform Context
{cloud_context}

## Example Output Format
{self.example_output}

## Your Task
Generate a complete architecture response in the exact JSON format shown in the example.
The response must be valid JSON that can be parsed directly.
Do not include any text before or after the JSON.
Do not wrap the JSON in markdown code blocks.

Focus on:
1. A clear, readable Mermaid diagram (flowchart TD) with proper node names
2. Specific compliance items for this use case and data classification
3. Cloud-specific deployment steps with actual service names
4. Production-quality sample code with proper error handling

Generate the JSON response now:"""

    async def generate(self, request: ArchitectureRequest) -> ArchitectureResponse:
        """Generate architecture using Claude."""

        user_prompt = self._build_user_prompt(request)
        logger.debug(f"Built prompt for use_case={request.use_case}, platform={request.cloud_platform}")

        message = self.client.messages.create(
            model=self.model,
            max_tokens=32768,
            system=[{
                "type": "text",
                "text": self.system_prompt,
                "cache_control": {"type": "ephemeral"}
            }],
            messages=[
                {"role": "user", "content": user_prompt}
            ],
        )

        # Check if response was truncated
        if message.stop_reason == "max_tokens":
            logger.warning("Response was truncated due to max_tokens limit")
            raise ValueError("Response exceeded maximum length. Please try a simpler configuration.")

        # Extract the response text
        response_text = message.content[0].text

        # Validate response size
        if len(response_text) > MAX_RESPONSE_SIZE:
            logger.error(f"Response too large: {len(response_text)} bytes")
            raise ValueError("Response too large")

        # Clean up the response if needed
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        # Parse JSON response
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            raise ValueError("Invalid response format from AI model")

        # Validate required keys exist
        required_keys = ["architecture", "compliance", "deployment", "sampleCode"]
        if not all(key in data for key in required_keys):
            missing = [k for k in required_keys if k not in data]
            logger.error(f"Missing required keys in response: {missing}")
            raise ValueError("Incomplete response from AI model")

        # Validate and return
        return ArchitectureResponse.model_validate(data)

    def _build_streaming_prompt(self, request: ArchitectureRequest) -> str:
        """Build the user prompt for streaming (excludes sampleCode)."""
        use_case_context = self._get_use_case_context(request.use_case)
        cloud_context = self._get_cloud_context(request.cloud_platform)

        return f"""Generate a healthcare reference architecture for:
- Use Case: {request.use_case.value}
- Cloud Platform: {request.cloud_platform.value}
- Integration Pattern: {request.integration_pattern.value}
- Data Classification: {request.data_classification.value}
- Scale Tier: {request.scale_tier.value}

## Healthcare Context
{self.healthcare_context}

{use_case_context}

## Cloud Platform Context
{cloud_context}

Return valid JSON with this structure (NO sampleCode - it will be generated separately):
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
  }}
}}

Return ONLY the JSON, no markdown or explanation."""

    async def generate_stream(self, request: ArchitectureRequest) -> AsyncGenerator[dict, None]:
        """Stream architecture generation with SSE events (excludes sampleCode)."""
        system_prompt_streaming = """You are an expert Healthcare IT Solutions Architect. Generate reference architectures with Mermaid diagrams, components, compliance checklists, and deployment steps in JSON format.

IMPORTANT: Do NOT include sampleCode in your response. Code samples will be generated separately on demand."""

        user_prompt = self._build_streaming_prompt(request)
        accumulated_text = ""
        emitted_sections = set()

        try:
            with self.client.messages.stream(
                model=self.model,
                max_tokens=24576,
                system=[{
                    "type": "text",
                    "text": system_prompt_streaming,
                    "cache_control": {"type": "ephemeral"}
                }],
                messages=[{"role": "user", "content": user_prompt}],
            ) as stream:
                for text in stream.text_stream:
                    accumulated_text += text

                    # Try to extract and emit completed sections
                    for section_name in ["architecture", "compliance", "deployment"]:
                        if section_name not in emitted_sections:
                            section_data = self._try_extract_section(accumulated_text, section_name)
                            if section_data is not None:
                                emitted_sections.add(section_name)
                                yield {
                                    "event": "section",
                                    "data": json.dumps({
                                        "section": section_name,
                                        "data": section_data
                                    })
                                }

            # Emit completion event
            yield {"event": "done", "data": json.dumps({"status": "complete"})}

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    def _try_extract_section(self, text: str, section_name: str) -> Optional[dict]:
        """Try to extract a complete JSON section from accumulated text."""
        pattern = rf'"{section_name}"\s*:\s*\{{'
        match = re.search(pattern, text)
        if not match:
            return None

        start_idx = match.end() - 1
        brace_count = 0
        in_string = False
        escape_next = False

        for i, char in enumerate(text[start_idx:], start_idx):
            if escape_next:
                escape_next = False
                continue
            if char == '\\':
                escape_next = True
                continue
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            if in_string:
                continue
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    section_text = text[start_idx:i + 1]
                    try:
                        return json.loads(section_text)
                    except json.JSONDecodeError:
                        return None

        return None

    async def generate_code(self, request: CodeGenerationRequest) -> CodeGenerationResponse:
        """Generate sample code based on architecture context."""
        system_prompt_code = """You are an expert Healthcare IT developer. Generate production-quality sample code for integrating with healthcare AI architectures. Include proper error handling, logging, and PHI compliance comments."""

        user_prompt = f"""Generate production-quality sample code for a healthcare AI integration:

Use Case: {request.use_case.value}
Cloud Platform: {request.cloud_platform.value}
Architecture Summary: {request.architecture_summary}

Return JSON with this structure:
{{
  "sampleCode": {{
    "python": "# Production Python code with error handling, logging, PHI compliance...",
    "typescript": "// Production TypeScript code with types, error handling, PHI compliance..."
  }}
}}

Requirements:
- Include proper error handling and logging
- Add PHI compliance comments where relevant
- Use cloud-specific SDK (boto3 for AWS, google-cloud for GCP)
- Include authentication and rate limiting
- Follow security best practices

Return ONLY the JSON, no markdown or explanation."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=16384,
            system=[{
                "type": "text",
                "text": system_prompt_code,
                "cache_control": {"type": "ephemeral"}
            }],
            messages=[{"role": "user", "content": user_prompt}],
        )

        response_text = message.content[0].text.strip()

        # Clean markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
        if response_text.endswith("```"):
            response_text = response_text.rsplit("```", 1)[0]
        response_text = response_text.strip()

        try:
            data = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse code response as JSON: {e}")
            raise ValueError("Invalid response format from AI model")

        return CodeGenerationResponse.model_validate(data)
