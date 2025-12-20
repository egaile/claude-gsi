"""
Tests for the Architecture Generator service.
"""

import json
import pytest
from unittest.mock import MagicMock, patch

from app.models import ArchitectureRequest, UseCase, CloudPlatform, IntegrationPattern, DataClassification, ScaleTier


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
