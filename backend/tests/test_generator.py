"""
Tests for the Architecture Generator service.
"""

import json
import pytest
from unittest.mock import MagicMock, patch

from app.models import AIProvider, ArchitectureRequest, UseCase, CloudPlatform, IntegrationPattern, DataClassification, ScaleTier


class TestArchitectureGenerator:
    """Tests for the ArchitectureGenerator class."""

    @pytest.fixture
    def sample_request(self):
        """Create a sample architecture request."""
        return ArchitectureRequest(
            use_case=UseCase.CLINICAL_DOCUMENTATION,
            cloud_platform=CloudPlatform.AWS_BEDROCK,
            integration_pattern=IntegrationPattern.API_GATEWAY,
            data_classification=DataClassification.PHI,
            scale_tier=ScaleTier.PRODUCTION
        )

    def test_generator_initialization(self, mock_anthropic_client):
        """Generator should initialize with API key."""
        from app.services.generator import ArchitectureGenerator

        generator = ArchitectureGenerator("sk-ant-api03-test-key")
        assert generator.client is not None
        assert generator.model == "claude-sonnet-4-20250514"

    def test_generator_loads_prompts(self, mock_anthropic_client):
        """Generator should load prompt files."""
        from app.services.generator import ArchitectureGenerator

        generator = ArchitectureGenerator("sk-ant-api03-test-key")
        # System prompt should be loaded (may be empty in test env)
        assert hasattr(generator, 'system_prompt')
        assert hasattr(generator, 'healthcare_context')

    def test_build_prompt_includes_ai_provider(self, mock_anthropic_client, sample_request):
        """Prompt should include the selected AI provider."""
        from app.services.generator import ArchitectureGenerator

        sample_request.ai_provider = AIProvider.OPENAI
        generator = ArchitectureGenerator("sk-ant-api03-test-key")
        prompt = generator._build_user_prompt(sample_request)

        assert "AI Provider" in prompt
        assert "openai" in prompt
        assert "OpenAI ChatGPT" in prompt

    @pytest.mark.asyncio
    async def test_generate_validates_response_structure(
        self, mock_anthropic_client, sample_request, sample_architecture_response
    ):
        """Generator should validate response has required keys."""
        from app.services.generator import ArchitectureGenerator

        # Mock the Claude response
        mock_message = MagicMock()
        mock_message.stop_reason = "end_turn"
        mock_message.content = [MagicMock(text=json.dumps(sample_architecture_response))]
        mock_anthropic_client.messages.create.return_value = mock_message

        generator = ArchitectureGenerator("sk-ant-api03-test-key")
        response = await generator.generate(sample_request)

        assert response is not None
        assert response.architecture is not None

    @pytest.mark.asyncio
    async def test_generate_rejects_truncated_response(
        self, mock_anthropic_client, sample_request
    ):
        """Generator should reject truncated responses."""
        from app.services.generator import ArchitectureGenerator

        # Mock truncated response
        mock_message = MagicMock()
        mock_message.stop_reason = "max_tokens"  # Indicates truncation
        mock_message.content = [MagicMock(text='{"partial": "data"}')]
        mock_anthropic_client.messages.create.return_value = mock_message

        generator = ArchitectureGenerator("sk-ant-api03-test-key")

        with pytest.raises(ValueError, match="exceeded maximum length"):
            await generator.generate(sample_request)

    @pytest.mark.asyncio
    async def test_generate_rejects_invalid_json(
        self, mock_anthropic_client, sample_request
    ):
        """Generator should reject invalid JSON responses."""
        from app.services.generator import ArchitectureGenerator

        # Mock invalid JSON response
        mock_message = MagicMock()
        mock_message.stop_reason = "end_turn"
        mock_message.content = [MagicMock(text='not valid json {')]
        mock_anthropic_client.messages.create.return_value = mock_message

        generator = ArchitectureGenerator("sk-ant-api03-test-key")

        with pytest.raises(ValueError, match="Invalid response format"):
            await generator.generate(sample_request)

    @pytest.mark.asyncio
    async def test_generate_rejects_missing_keys(
        self, mock_anthropic_client, sample_request
    ):
        """Generator should reject responses missing required keys."""
        from app.services.generator import ArchitectureGenerator

        # Mock response missing required keys
        mock_message = MagicMock()
        mock_message.stop_reason = "end_turn"
        mock_message.content = [MagicMock(text='{"architecture": {}}')]  # Missing other keys
        mock_anthropic_client.messages.create.return_value = mock_message

        generator = ArchitectureGenerator("sk-ant-api03-test-key")

        with pytest.raises(ValueError, match="Incomplete response"):
            await generator.generate(sample_request)

    @pytest.mark.asyncio
    async def test_generate_handles_markdown_wrapped_json(
        self, mock_anthropic_client, sample_request, sample_architecture_response
    ):
        """Generator should handle JSON wrapped in markdown code blocks."""
        from app.services.generator import ArchitectureGenerator

        # Mock response with markdown
        wrapped_json = f"```json\n{json.dumps(sample_architecture_response)}\n```"
        mock_message = MagicMock()
        mock_message.stop_reason = "end_turn"
        mock_message.content = [MagicMock(text=wrapped_json)]
        mock_anthropic_client.messages.create.return_value = mock_message

        generator = ArchitectureGenerator("sk-ant-api03-test-key")
        response = await generator.generate(sample_request)

        assert response is not None

    @pytest.mark.asyncio
    async def test_generate_uses_openai_when_selected(
        self, sample_request, sample_architecture_response
    ):
        """Generator should route requests to OpenAI when selected."""
        from app.services import generator as generator_module
        from app.services.generator import ArchitectureGenerator

        sample_request.ai_provider = AIProvider.OPENAI

        with patch.object(generator_module, "OpenAI") as mock_openai:
            openai_client = MagicMock()
            mock_openai.return_value = openai_client

            mock_choice = MagicMock()
            mock_choice.message.content = json.dumps(sample_architecture_response)
            mock_choice.finish_reason = "stop"
            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            openai_client.chat.completions.create.return_value = mock_response

            generator = ArchitectureGenerator(openai_api_key="sk-test-openai-key-for-testing")
            response = await generator.generate(sample_request)

            assert response.architecture is not None
            openai_client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_stream_caches_parallel_sections(
        self, mock_anthropic_client, sample_request
    ):
        """Streaming should cache completed sections for repeated configurations."""
        from app.services.generator import ArchitectureGenerator

        generator = ArchitectureGenerator("sk-ant-api03-test-key")
        section_data = {
            "architecture": {
                "mermaidDiagram": "flowchart TD\nA --> B",
                "components": [],
                "dataFlows": [],
            },
            "compliance": {
                "checklist": [],
                "baaRequirements": "BAA required",
            },
            "deployment": {
                "steps": [],
                "iamPolicies": [],
                "networkConfig": "VPC",
                "monitoringSetup": "Logs",
            },
        }

        with patch.object(
            generator,
            "_generate_section_sync",
            side_effect=lambda _request, section_name: section_data[section_name],
        ) as mock_generate_section:
            first_events = [event async for event in generator.generate_stream(sample_request)]
            second_events = [event async for event in generator.generate_stream(sample_request)]

        assert mock_generate_section.call_count == 3
        assert sum(event.get("event") == "section" for event in first_events) == 3
        assert sum(event.get("event") == "section" for event in second_events) == 3
        cached_payloads = [
            json.loads(event["data"])
            for event in second_events
            if event.get("event") == "section"
        ]
        assert all(payload.get("cached") is True for payload in cached_payloads)

    def test_normalizes_compliance_section_variants(self, mock_anthropic_client):
        """Compliance section validation should tolerate common model labels."""
        from app.services.generator import ArchitectureGenerator

        generator = ArchitectureGenerator("sk-ant-api03-test-key")
        section = generator._normalize_and_validate_section(
            "compliance",
            {
                "checklist": [
                    {
                        "category": "privacy",
                        "requirement": "BAA",
                        "implementation": "Execute agreements",
                        "priority": "high",
                    },
                    {
                        "category": "security",
                        "requirement": "Audit logs",
                        "implementation": "Enable logging",
                        "priority": "nice-to-have",
                    },
                ],
                "baaRequirements": "Required",
            },
        )

        assert section["checklist"][0]["category"] == "administrative"
        assert section["checklist"][0]["priority"] == "required"
        assert section["checklist"][1]["category"] == "technical"
        assert section["checklist"][1]["priority"] == "recommended"

    def test_deployment_section_accepts_structured_iam_policies(self, mock_anthropic_client):
        """Deployment section should accept structured IAM policy objects."""
        from app.services.generator import ArchitectureGenerator

        generator = ArchitectureGenerator("sk-ant-api03-test-key")
        section = generator._normalize_and_validate_section(
            "deployment",
            {
                "steps": ["Deploy service"],
                "iamPolicies": [
                    {
                        "name": "LambdaExecution",
                        "policy": {
                            "Version": "2012-10-17",
                            "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}],
                        },
                    }
                ],
                "networkConfig": "Private subnets",
                "monitoringSetup": "CloudWatch",
            },
        )

        assert isinstance(section["iamPolicies"][0], dict)
        assert section["iamPolicies"][0]["name"] == "LambdaExecution"


class TestResponseSizeLimit:
    """Tests for response size validation."""

    @pytest.mark.asyncio
    async def test_rejects_oversized_response(self, mock_anthropic_client):
        """Should reject responses exceeding size limit."""
        from app.services.generator import ArchitectureGenerator, MAX_RESPONSE_SIZE

        # Create oversized response
        large_text = "x" * (MAX_RESPONSE_SIZE + 1000)
        mock_message = MagicMock()
        mock_message.stop_reason = "end_turn"
        mock_message.content = [MagicMock(text=large_text)]
        mock_anthropic_client.messages.create.return_value = mock_message

        generator = ArchitectureGenerator("sk-ant-api03-test-key")
        request = ArchitectureRequest(
            use_case=UseCase.CLINICAL_DOCUMENTATION,
            cloud_platform=CloudPlatform.AWS_BEDROCK,
            integration_pattern=IntegrationPattern.API_GATEWAY,
            data_classification=DataClassification.PHI,
            scale_tier=ScaleTier.PRODUCTION
        )

        with pytest.raises(ValueError, match="too large"):
            await generator.generate(request)
