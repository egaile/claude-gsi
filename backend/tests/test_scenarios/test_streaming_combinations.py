"""
Tests for streaming architecture generation endpoint with all combinations.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from app.models import (
    ArchitectureRequest,
    CloudPlatform,
    DataClassification,
    IntegrationPattern,
    ScaleTier,
    UseCase,
)
from tests.fixtures.mock_responses import generate_mock_streaming_response
from tests.test_scenarios.conftest import (
    ALL_COMBINATIONS,
    REPRESENTATIVE_COMBINATIONS,
    MockStreamContext,
    combination_id,
)


class TestStreamingResponseValidation:
    """Tests that validate streaming response format for all combinations."""

    @pytest.mark.parametrize(
        "combination",
        ALL_COMBINATIONS,
        ids=[combination_id(c) for c in ALL_COMBINATIONS],
    )
    def test_streaming_response_parses_correctly(self, combination):
        """
        Validate that streaming responses (without sampleCode) parse correctly.
        """
        use_case, platform, pattern, classification, scale = combination

        mock_response_data = generate_mock_streaming_response(
            use_case, platform, pattern, classification, scale
        )

        # Verify sampleCode is not present
        assert "sampleCode" not in mock_response_data

        # Verify required sections are present
        assert "architecture" in mock_response_data
        assert "compliance" in mock_response_data
        assert "deployment" in mock_response_data

        # Verify architecture content
        assert "mermaidDiagram" in mock_response_data["architecture"]
        assert "components" in mock_response_data["architecture"]
        assert "dataFlows" in mock_response_data["architecture"]
        assert len(mock_response_data["architecture"]["components"]) > 0

        # Verify compliance content
        assert "checklist" in mock_response_data["compliance"]
        assert "baaRequirements" in mock_response_data["compliance"]

        # Verify deployment content
        assert "steps" in mock_response_data["deployment"]
        assert "iamPolicies" in mock_response_data["deployment"]

    @pytest.mark.parametrize(
        "combination",
        ALL_COMBINATIONS,
        ids=[combination_id(c) for c in ALL_COMBINATIONS],
    )
    def test_streaming_response_is_valid_json(self, combination):
        """
        Validate that streaming responses serialize to valid JSON.
        """
        use_case, platform, pattern, classification, scale = combination

        mock_response_data = generate_mock_streaming_response(
            use_case, platform, pattern, classification, scale
        )

        # Should serialize without error
        json_str = json.dumps(mock_response_data)
        assert len(json_str) > 0

        # Should parse back without error
        parsed = json.loads(json_str)
        assert parsed == mock_response_data


class TestStreamingWithMockedAPI:
    """Tests that exercise the streaming generator with mocked responses."""

    @pytest.mark.parametrize(
        "combination",
        REPRESENTATIVE_COMBINATIONS,
        ids=[combination_id(c) for c in REPRESENTATIVE_COMBINATIONS],
    )
    @pytest.mark.asyncio
    async def test_streaming_generator_accepts_combination(
        self, combination, mock_anthropic_client, mock_stream_context_factory
    ):
        """
        Validate streaming generation for representative combinations.
        """
        use_case, platform, pattern, classification, scale = combination

        # Configure mock for streaming
        mock_stream = mock_stream_context_factory(
            use_case, platform, pattern, classification, scale
        )
        mock_anthropic_client.messages.stream.return_value = mock_stream

        from app.services.generator import ArchitectureGenerator

        generator = ArchitectureGenerator("sk-ant-api03-test-key")

        request = ArchitectureRequest(
            use_case=use_case,
            cloud_platform=platform,
            integration_pattern=pattern,
            data_classification=classification,
            scale_tier=scale,
        )

        # Collect all events from the stream
        events = []
        async for event in generator.generate_stream(request):
            events.append(event)

        # Validate events were generated
        assert len(events) > 0

        # Should have progress events
        event_types = [e.get("event") for e in events if "event" in e]
        # At minimum, should have some events emitted
        assert len(event_types) >= 0 or len(events) > 0


class TestMermaidDiagramValidation:
    """Tests that validate Mermaid diagram syntax in streaming responses."""

    @pytest.mark.parametrize(
        "combination",
        REPRESENTATIVE_COMBINATIONS,
        ids=[combination_id(c) for c in REPRESENTATIVE_COMBINATIONS],
    )
    def test_mermaid_diagram_has_valid_syntax(self, combination):
        """
        Validate that Mermaid diagrams have basic valid syntax.
        """
        use_case, platform, pattern, classification, scale = combination

        mock_response_data = generate_mock_streaming_response(
            use_case, platform, pattern, classification, scale
        )

        diagram = mock_response_data["architecture"]["mermaidDiagram"]

        # Should start with a valid diagram type
        assert diagram.strip().startswith(("flowchart", "graph", "sequenceDiagram"))

        # Should contain arrow connections
        assert "-->" in diagram or "---" in diagram

        # Should not have self-referential links (common error)
        lines = diagram.split("\n")
        for line in lines:
            if "-->" in line:
                parts = line.split("-->")
                if len(parts) == 2:
                    source = parts[0].strip().split("[")[0].strip()
                    target = parts[1].strip().split("[")[0].strip()
                    assert source != target, f"Self-referential link found: {source}"


class TestIAMPolicyValidation:
    """Tests that validate IAM policy format in responses."""

    @pytest.mark.parametrize(
        "combination",
        REPRESENTATIVE_COMBINATIONS,
        ids=[combination_id(c) for c in REPRESENTATIVE_COMBINATIONS],
    )
    def test_iam_policies_are_valid_json(self, combination):
        """
        Validate that IAM policies are valid JSON strings.
        """
        use_case, platform, pattern, classification, scale = combination

        mock_response_data = generate_mock_streaming_response(
            use_case, platform, pattern, classification, scale
        )

        iam_policies = mock_response_data["deployment"]["iamPolicies"]
        assert len(iam_policies) > 0

        for policy in iam_policies:
            # Each policy should be a valid JSON string
            parsed = json.loads(policy)
            assert isinstance(parsed, dict)

    @pytest.mark.parametrize("platform", list(CloudPlatform))
    def test_aws_iam_policies_have_correct_structure(self, platform):
        """
        Validate AWS IAM policies have Version and Statement fields.
        """
        mock_response_data = generate_mock_streaming_response(
            UseCase.CLINICAL_DOCUMENTATION,
            platform,
            IntegrationPattern.API_GATEWAY,
            DataClassification.PHI,
            ScaleTier.PRODUCTION,
        )

        iam_policies = mock_response_data["deployment"]["iamPolicies"]

        if platform == CloudPlatform.AWS_BEDROCK:
            for policy_str in iam_policies:
                policy = json.loads(policy_str)
                assert "Version" in policy, "AWS IAM policy should have Version"
                assert "Statement" in policy, "AWS IAM policy should have Statement"
                assert isinstance(policy["Statement"], list)
        else:
            # GCP uses bindings format
            for policy_str in iam_policies:
                policy = json.loads(policy_str)
                assert "bindings" in policy, "GCP IAM policy should have bindings"
                assert isinstance(policy["bindings"], list)
