"""
Architecture Generator Service

Integrates with configured AI providers to generate healthcare reference architectures.
"""

import json
import logging
import os
import re
import asyncio
from pathlib import Path
from typing import AsyncGenerator, Optional

import anthropic

try:
    import openai
    from openai import OpenAI
except ImportError:  # pragma: no cover - handled at runtime when provider is selected
    openai = None
    OpenAI = None

from app.models import (
    AIProvider,
    ArchitectureRequest,
    ArchitectureResponse,
    CodeGenerationRequest,
    CodeGenerationResponse,
    UseCase,
    CloudPlatform,
)

logger = logging.getLogger(__name__)

# Constants
MAX_RESPONSE_SIZE = 500_000  # 500KB limit for model responses
STREAMING_SECTIONS = ("architecture", "compliance", "deployment")


class ArchitectureGenerator:
    """Generates healthcare reference architectures using the selected AI provider."""

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
    ):
        # Add timeouts to prevent hanging requests (120 seconds)
        self.anthropic_client = (
            anthropic.Anthropic(api_key=anthropic_api_key, timeout=120.0)
            if anthropic_api_key
            else None
        )
        self.openai_client = (
            OpenAI(api_key=openai_api_key, timeout=120.0)
            if openai_api_key and OpenAI is not None
            else None
        )
        # Backwards-compatible aliases used by existing tests and integrations.
        self.client = self.anthropic_client
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-5.2")
        self.prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        self.templates_dir = Path(__file__).parent.parent.parent / "templates"
        self._stream_cache: dict[str, dict[str, dict]] = {}
        
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

    def _get_ai_provider_context(self, provider: AIProvider) -> str:
        """Get provider-specific architecture guidance."""
        if provider == AIProvider.OPENAI:
            return f"""
## AI Provider Context: OpenAI ChatGPT

- Use OpenAI ChatGPT models as the LLM endpoint.
- Default backend model is configurable with OPENAI_MODEL; current default is {self.openai_model}.
- Store OPENAI_API_KEY in the backend secret manager for the selected cloud.
- For PHI workloads, require an appropriate OpenAI agreement/BAA and confirm healthcare data handling controls before production use.
- In diagrams and code, label the LLM component as OpenAI ChatGPT or OpenAI API.
- Do not use Claude-specific request formats, model IDs, SDK imports, or service names in generated sample code.
"""

    def _request_cache_key(self, request: ArchitectureRequest, suffix: str) -> str:
        """Create a stable cache key for a request."""
        request_data = request.model_dump(mode="json", by_alias=True)
        return f"{suffix}:{json.dumps(request_data, sort_keys=True)}"

    @staticmethod
    def _strip_markdown_fences(response_text: str) -> str:
        """Clean optional markdown fences from model JSON output."""
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
        if response_text.endswith("```"):
            response_text = response_text.rsplit("```", 1)[0]
        return response_text.strip()

        return f"""
## AI Provider Context: Claude

- Use Claude models as the LLM endpoint.
- Default backend model is configurable with ANTHROPIC_MODEL; current default is {self.model}.
- Store ANTHROPIC_API_KEY in the backend secret manager for the selected cloud unless using a cloud-managed Claude endpoint.
- For PHI workloads, require an appropriate Anthropic/cloud provider BAA and confirm healthcare data handling controls before production use.
- In diagrams and code, label the LLM component as Claude.
- Do not use OpenAI-specific request formats, model IDs, SDK imports, or service names in generated sample code.
"""

    def _ensure_provider_configured(self, provider: AIProvider) -> None:
        """Ensure the selected provider has a configured client."""
        if provider == AIProvider.OPENAI:
            if OpenAI is None:
                raise ValueError("OpenAI SDK is not installed")
            if self.openai_client is None:
                raise ValueError("Selected AI provider is not configured")
            return

        if self.anthropic_client is None:
            raise ValueError("Selected AI provider is not configured")

    def _create_completion(
        self,
        provider: AIProvider,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
    ) -> tuple[str, Optional[str]]:
        """Create a non-streaming completion and return text plus finish reason."""
        self._ensure_provider_configured(provider)

        if provider == AIProvider.OPENAI:
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                max_completion_tokens=max_tokens,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            choice = response.choices[0]
            return choice.message.content or "", choice.finish_reason

        message = self.anthropic_client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=[{
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"}
            }],
            messages=[
                {"role": "user", "content": user_prompt}
            ],
        )
        return message.content[0].text, message.stop_reason

    def _stream_completion(
        self,
        provider: AIProvider,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
    ):
        """Yield text chunks from the selected provider."""
        self._ensure_provider_configured(provider)

        if provider == AIProvider.OPENAI:
            stream = self.openai_client.chat.completions.create(
                model=self.openai_model,
                max_completion_tokens=max_tokens,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                stream=True,
            )
            for chunk in stream:
                if chunk.choices:
                    text = chunk.choices[0].delta.content
                    if text:
                        yield text
            return

        with self.anthropic_client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            system=[{
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"}
            }],
            messages=[{"role": "user", "content": user_prompt}],
        ) as stream:
            for text in stream.text_stream:
                yield text

    def _build_user_prompt(self, request: ArchitectureRequest) -> str:
        """Build the user prompt for the selected AI provider."""
        use_case_context = self._get_use_case_context(request.use_case)
        cloud_context = self._get_cloud_context(request.cloud_platform)
        ai_provider_context = self._get_ai_provider_context(request.ai_provider)

        return f"""Generate a complete reference architecture for the following configuration:

## Configuration
- **Use Case**: {request.use_case.value}
- **Deployment Cloud**: {request.cloud_platform.value}
- **AI Provider**: {request.ai_provider.value}
- **Integration Pattern**: {request.integration_pattern.value}
- **Data Classification**: {request.data_classification.value}
- **Scale Tier**: {request.scale_tier.value}

## Healthcare Context
{self.healthcare_context}

{use_case_context}

## Cloud Platform Context
{cloud_context}

{ai_provider_context}

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
5. Use the selected AI provider consistently throughout diagrams, component names, BAA guidance, and sample code

Generate the JSON response now:"""

    async def generate(self, request: ArchitectureRequest) -> ArchitectureResponse:
        """Generate architecture using the selected AI provider."""

        user_prompt = self._build_user_prompt(request)
        logger.debug(
            "Built prompt for use_case=%s, platform=%s, provider=%s",
            request.use_case,
            request.cloud_platform,
            request.ai_provider,
        )

        response_text, finish_reason = self._create_completion(
            request.ai_provider,
            self.system_prompt,
            user_prompt,
            32768,
        )

        # Check if response was truncated
        if finish_reason in {"max_tokens", "length"}:
            logger.warning("Response was truncated due to max_tokens limit")
            raise ValueError("Response exceeded maximum length. Please try a simpler configuration.")

        # Validate response size
        if len(response_text) > MAX_RESPONSE_SIZE:
            logger.error(f"Response too large: {len(response_text)} bytes")
            raise ValueError("Response too large")

        # Clean up the response if needed
        response_text = self._strip_markdown_fences(response_text)

        # Parse JSON response
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI model response as JSON: {e}")
            raise ValueError("Invalid response format from AI model")

        # Validate required keys exist
        required_keys = ["architecture", "compliance", "deployment", "sampleCode"]
        if not all(key in data for key in required_keys):
            missing = [k for k in required_keys if k not in data]
            logger.error(f"Missing required keys in response: {missing}")
            raise ValueError("Incomplete response from AI model")

        # Validate and return
        return ArchitectureResponse.model_validate(data)

    def _build_section_prompt(self, request: ArchitectureRequest, section_name: str) -> str:
        """Build a prompt for one streamable response section."""
        use_case_context = self._get_use_case_context(request.use_case)
        cloud_context = self._get_cloud_context(request.cloud_platform)
        ai_provider_context = self._get_ai_provider_context(request.ai_provider)
        section_formats = {
            "architecture": """
{
  "mermaidDiagram": "flowchart TD...",
  "components": [{"name": "", "service": "", "purpose": "", "phiTouchpoint": true}],
  "dataFlows": [{"from": "", "to": "", "data": "", "encrypted": true}]
}
""",
            "compliance": """
{
  "checklist": [{"category": "technical", "requirement": "", "implementation": "", "priority": "required"}],
  "baaRequirements": ""
}
""",
            "deployment": """
{
  "steps": [],
  "iamPolicies": [],
  "networkConfig": "",
  "monitoringSetup": ""
}
""",
        }

        section_guidance = {
            "architecture": "Generate the architecture section only. Keep Mermaid node labels short and move detail into components and dataFlows.",
            "compliance": "Generate the compliance section only. Focus on HIPAA, PHI handling, BAA, audit, and human review controls.",
            "deployment": "Generate the deployment section only. Include concrete cloud steps, IAM policies, network config, and monitoring setup.",
        }

        return f"""Generate one JSON section for a healthcare reference architecture.

## Section
{section_name}

## Section Task
{section_guidance[section_name]}

## Configuration
- Use Case: {request.use_case.value}
- Deployment Cloud: {request.cloud_platform.value}
- AI Provider: {request.ai_provider.value}
- Integration Pattern: {request.integration_pattern.value}
- Data Classification: {request.data_classification.value}
- Scale Tier: {request.scale_tier.value}

## Healthcare Context
{self.healthcare_context}

{use_case_context}

## Cloud Platform Context
{cloud_context}

{ai_provider_context}

## Required JSON Shape
{section_formats[section_name]}

Return ONLY this section's JSON object, no parent key, no markdown, no explanation.
The response must be valid JSON. Use the selected AI provider consistently."""

    def _build_streaming_prompt(self, request: ArchitectureRequest) -> str:
        """Build the legacy full streaming prompt (excludes sampleCode)."""
        section_shapes = {
            "architecture": self._build_section_prompt(request, "architecture"),
            "compliance": self._build_section_prompt(request, "compliance"),
            "deployment": self._build_section_prompt(request, "deployment"),
        }
        return "\n\n".join(section_shapes.values())

    def _generate_section_sync(self, request: ArchitectureRequest, section_name: str) -> dict:
        """Generate one response section synchronously for thread execution."""
        system_prompt_section = """You are an expert Healthcare IT Solutions Architect. Generate one valid JSON section for a healthcare AI reference architecture. Keep the section concise, schema-compliant, and production-oriented."""
        user_prompt = self._build_section_prompt(request, section_name)
        response_text, finish_reason = self._create_completion(
            request.ai_provider,
            system_prompt_section,
            user_prompt,
            8192,
        )

        if finish_reason in {"max_tokens", "length"}:
            raise ValueError(f"{section_name} section exceeded maximum length")

        if len(response_text) > MAX_RESPONSE_SIZE:
            raise ValueError(f"{section_name} section response too large")

        response_text = self._strip_markdown_fences(response_text)

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse %s section response as JSON: %s", section_name, e)
            raise ValueError("Invalid response format from AI model") from e

    async def generate_stream(self, request: ArchitectureRequest) -> AsyncGenerator[dict, None]:
        """Stream architecture generation with parallel section calls and SSE events."""
        cache_key = self._request_cache_key(request, "stream-sections-v2")

        try:
            # Send immediate "started" event so UI shows activity
            yield {
                "event": "started",
                "data": json.dumps({"status": "generating", "mode": "parallel-sections"}),
            }

            cached_sections = self._stream_cache.get(cache_key)
            if cached_sections:
                logger.info("Using cached architecture sections")
                for section_name in STREAMING_SECTIONS:
                    yield {
                        "event": "section",
                        "data": json.dumps({
                            "section": section_name,
                            "data": cached_sections[section_name],
                            "cached": True,
                        }),
                    }
                yield {"event": "done", "data": json.dumps({"status": "complete", "cached": True})}
                return

            async def generate_section(section_name: str) -> tuple[str, dict]:
                section_data = await asyncio.to_thread(
                    self._generate_section_sync,
                    request,
                    section_name,
                )
                return section_name, section_data

            tasks = [
                asyncio.create_task(generate_section(section_name))
                for section_name in STREAMING_SECTIONS
            ]
            generated_sections: dict[str, dict] = {}

            for task in asyncio.as_completed(tasks):
                section_name, section_data = await task
                generated_sections[section_name] = section_data
                yield {
                    "event": "section",
                    "data": json.dumps({
                        "section": section_name,
                        "data": section_data,
                    }),
                }

            if all(section_name in generated_sections for section_name in STREAMING_SECTIONS):
                self._stream_cache[cache_key] = {
                    section_name: generated_sections[section_name]
                    for section_name in STREAMING_SECTIONS
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
        ai_provider_context = self._get_ai_provider_context(request.ai_provider)

        user_prompt = f"""Generate production-quality sample code for a healthcare AI integration:

Use Case: {request.use_case.value}
Deployment Cloud: {request.cloud_platform.value}
AI Provider: {request.ai_provider.value}
Architecture Summary: {request.architecture_summary}

{ai_provider_context}

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
- Use the selected AI provider SDK/API and cloud-specific SDK where relevant (boto3 for AWS, google-cloud for GCP)
- Include authentication and rate limiting
- Follow security best practices
- Do not mix provider-specific SDKs or request formats

Return ONLY the JSON, no markdown or explanation."""

        response_text, _ = self._create_completion(
            request.ai_provider,
            system_prompt_code,
            user_prompt,
            16384,
        )

        response_text = response_text.strip()

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
