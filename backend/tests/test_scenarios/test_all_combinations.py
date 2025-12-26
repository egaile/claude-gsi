"""
Tests for all 288 architecture generation combinations.

This module validates that:
1. All input combinations are accepted by the API
2. Responses parse correctly into Pydantic models
3. No unexpected errors occur for any valid combination
"""

import asyncio
import json
from unittest.mock import MagicMock, patch

import pytest

from app.models import (
    ArchitectureRequest,
    ArchitectureResponse,
    CloudPlatform,
    DataClassification,
    IntegrationPattern,
    ScaleTier,
    UseCase,
)
from tests.fixtures.mock_responses import generate_mock_architecture_response
from tests.test_scenarios.conftest import ALL_COMBINATIONS, combination_id


class TestRequestModelValidation:
    """Fast tests that validate request model accepts all combinations."""

    @pytest.mark.parametrize(
        "combination",
        ALL_COMBINATIONS,
        ids=[combination_id(c) for c in ALL_COMBINATIONS],
    )
    def test_request_model_accepts_combination(self, combination):
        """
        Validate that ArchitectureRequest model accepts all combinations.
        This is a fast sanity check that runs without mocking.
        """
        use_case, platform, pattern, classification, scale = combination

        # This should not raise any validation errors
        request = ArchitectureRequest(
            use_case=use_case,
            cloud_platform=platform,
            integration_pattern=pattern,
            data_classification=classification,
            scale_tier=scale,
        )

        assert request.use_case == use_case
        assert request.cloud_platform == platform
        assert request.integration_pattern == pattern
        assert request.data_classification == classification
        assert request.scale_tier == scale


class TestResponseSerialization:
    """Tests that validate mock responses serialize correctly."""

    @pytest.mark.parametrize(
        "combination",
        ALL_COMBINATIONS,
        ids=[combination_id(c) for c in ALL_COMBINATIONS],
    )
    def test_response_parses_correctly(self, combination):
        """
        Validate that mock responses parse into Pydantic models.
        """
        use_case, platform, pattern, classification, scale = combination

        mock_response_data = generate_mock_architecture_response(
            use_case, platform, pattern, classification, scale
        )

        # Parse as Pydantic model - should not raise
        response = ArchitectureResponse.model_validate(mock_response_data)

        # Validate required fields exist
        assert response.architecture is not None
        assert response.compliance is not None
        assert response.deployment is not None
        assert response.sample_code is not None

        # Validate architecture content
        assert response.architecture.mermaid_diagram is not None
        assert len(response.architecture.components) > 0
        assert len(response.architecture.data_flows) > 0

        # Validate compliance content
        assert len(response.compliance.checklist) > 0
        assert response.compliance.baa_requirements is not None

        # Validate deployment content
        assert len(response.deployment.steps) > 0
        assert len(response.deployment.iam_policies) > 0
        assert response.deployment.network_config is not None
        assert response.deployment.monitoring_setup is not None

    @pytest.mark.parametrize(
        "combination",
        ALL_COMBINATIONS,
        ids=[combination_id(c) for c in ALL_COMBINATIONS],
    )
    def test_response_serializes_with_camel_case(self, combination):
        """
        Validate that responses serialize with camelCase aliases.
        """
        use_case, platform, pattern, classification, scale = combination

        mock_response_data = generate_mock_architecture_response(
            use_case, platform, pattern, classification, scale
        )

        # Parse as Pydantic model
        response = ArchitectureResponse.model_validate(mock_response_data)

        # Serialize back to dict with aliases
        serialized = response.model_dump(by_alias=True)

        # Verify camelCase keys
        assert "sampleCode" in serialized
        assert "mermaidDiagram" in serialized["architecture"]
        assert "dataFlows" in serialized["architecture"]
        assert "baaRequirements" in serialized["compliance"]
        assert "iamPolicies" in serialized["deployment"]
        assert "networkConfig" in serialized["deployment"]
        assert "monitoringSetup" in serialized["deployment"]

        # Verify components have correct aliases
        for component in serialized["architecture"]["components"]:
            assert "phiTouchpoint" in component


class TestGeneratorWithMockedAPI:
    """Tests that exercise the generator with mocked Claude responses."""

    @pytest.mark.parametrize(
        "combination",
        ALL_COMBINATIONS,
        ids=[combination_id(c) for c in ALL_COMBINATIONS],
    )
    def test_generator_accepts_combination(
        self, combination, mock_anthropic_client, mock_claude_response_factory
    ):
        """
        Validate that the generator works for each combination.
        """
        use_case, platform, pattern, classification, scale = combination

        # Configure mock to return appropriate response
        mock_response = mock_claude_response_factory(
            use_case, platform, pattern, classification, scale
        )
        mock_anthropic_client.messages.create.return_value = mock_response

        # Import generator after mock is configured
        from app.services.generator import ArchitectureGenerator

        generator = ArchitectureGenerator("sk-ant-api03-test-key")

        # Create request
        request = ArchitectureRequest(
            use_case=use_case,
            cloud_platform=platform,
            integration_pattern=pattern,
            data_classification=classification,
            scale_tier=scale,
        )

        # Execute
        response = asyncio.run(generator.generate(request))

        # Validate response structure
        assert response is not None
        assert isinstance(response, ArchitectureResponse)
        assert response.architecture is not None
        assert response.compliance is not None
        assert response.deployment is not None
        assert response.sample_code is not None

        # Validate response contains expected content
        assert len(response.architecture.components) > 0
        assert len(response.architecture.data_flows) > 0
        assert len(response.compliance.checklist) > 0
        assert len(response.deployment.steps) > 0


class TestPHITouchpoints:
    """Tests that validate PHI touchpoint handling."""

    @pytest.mark.parametrize("use_case", list(UseCase))
    def test_phi_data_has_phi_touchpoints(
        self, use_case, mock_anthropic_client, mock_claude_response_factory
    ):
        """Test that PHI data classification results in PHI touchpoints."""
        mock_response = mock_claude_response_factory(
            use_case,
            CloudPlatform.AWS_BEDROCK,
            IntegrationPattern.API_GATEWAY,
            DataClassification.PHI,
            ScaleTier.PRODUCTION,
        )
        mock_anthropic_client.messages.create.return_value = mock_response

        from app.services.generator import ArchitectureGenerator

        generator = ArchitectureGenerator("sk-ant-api03-test-key")
        request = ArchitectureRequest(
            use_case=use_case,
            cloud_platform=CloudPlatform.AWS_BEDROCK,
            integration_pattern=IntegrationPattern.API_GATEWAY,
            data_classification=DataClassification.PHI,
            scale_tier=ScaleTier.PRODUCTION,
        )

        response = asyncio.run(generator.generate(request))

        # PHI data classification should have PHI touchpoints marked
        phi_touchpoints = [c for c in response.architecture.components if c.phi_touchpoint]
        assert len(phi_touchpoints) > 0, f"PHI classification should have touchpoints for {use_case}"

    @pytest.mark.parametrize("use_case", list(UseCase))
    def test_public_data_has_no_phi_touchpoints(
        self, use_case, mock_anthropic_client, mock_claude_response_factory
    ):
        """Test that public data classification has no PHI touchpoints."""
        mock_response = mock_claude_response_factory(
            use_case,
            CloudPlatform.GCP_VERTEX,
            IntegrationPattern.API_GATEWAY,
            DataClassification.PUBLIC,
            ScaleTier.PILOT,
        )
        mock_anthropic_client.messages.create.return_value = mock_response

        from app.services.generator import ArchitectureGenerator

        generator = ArchitectureGenerator("sk-ant-api03-test-key")
        request = ArchitectureRequest(
            use_case=use_case,
            cloud_platform=CloudPlatform.GCP_VERTEX,
            integration_pattern=IntegrationPattern.API_GATEWAY,
            data_classification=DataClassification.PUBLIC,
            scale_tier=ScaleTier.PILOT,
        )

        response = asyncio.run(generator.generate(request))

        # Public data should not have PHI touchpoints
        phi_touchpoints = [c for c in response.architecture.components if c.phi_touchpoint]
        assert len(phi_touchpoints) == 0, f"Public classification should not have PHI touchpoints for {use_case}"


class TestCloudPlatformSpecificContent:
    """Tests that validate cloud platform-specific content."""

    @pytest.mark.parametrize("use_case", list(UseCase))
    def test_aws_responses_contain_aws_services(
        self, use_case, mock_anthropic_client, mock_claude_response_factory
    ):
        """Test that AWS platform responses mention AWS services."""
        mock_response = mock_claude_response_factory(
            use_case,
            CloudPlatform.AWS_BEDROCK,
            IntegrationPattern.API_GATEWAY,
            DataClassification.PHI,
            ScaleTier.PRODUCTION,
        )
        mock_anthropic_client.messages.create.return_value = mock_response

        from app.services.generator import ArchitectureGenerator

        generator = ArchitectureGenerator("sk-ant-api03-test-key")
        request = ArchitectureRequest(
            use_case=use_case,
            cloud_platform=CloudPlatform.AWS_BEDROCK,
            integration_pattern=IntegrationPattern.API_GATEWAY,
            data_classification=DataClassification.PHI,
            scale_tier=ScaleTier.PRODUCTION,
        )

        response = asyncio.run(generator.generate(request))

        # Check for AWS-specific services in components
        all_services = [c.service for c in response.architecture.components]
        services_str = " ".join(all_services).lower()
        assert "aws" in services_str or "amazon" in services_str or "bedrock" in services_str

    @pytest.mark.parametrize("use_case", list(UseCase))
    def test_gcp_responses_contain_gcp_services(
        self, use_case, mock_anthropic_client, mock_claude_response_factory
    ):
        """Test that GCP platform responses mention GCP services."""
        mock_response = mock_claude_response_factory(
            use_case,
            CloudPlatform.GCP_VERTEX,
            IntegrationPattern.API_GATEWAY,
            DataClassification.PHI,
            ScaleTier.PRODUCTION,
        )
        mock_anthropic_client.messages.create.return_value = mock_response

        from app.services.generator import ArchitectureGenerator

        generator = ArchitectureGenerator("sk-ant-api03-test-key")
        request = ArchitectureRequest(
            use_case=use_case,
            cloud_platform=CloudPlatform.GCP_VERTEX,
            integration_pattern=IntegrationPattern.API_GATEWAY,
            data_classification=DataClassification.PHI,
            scale_tier=ScaleTier.PRODUCTION,
        )

        response = asyncio.run(generator.generate(request))

        # Check for GCP-specific services in components
        all_services = [c.service for c in response.architecture.components]
        services_str = " ".join(all_services).lower()
        assert "cloud" in services_str or "vertex" in services_str or "gcp" in services_str
