"""
Integration tests that call the actual Claude API.

These tests validate real API responses for:
- JSON parsing correctness
- Mermaid diagram syntax
- IAM policy structure
- All required fields presence

Run with: pytest -m integration tests/test_scenarios/test_integration_real_api.py -v

Note: These tests require ANTHROPIC_API_KEY environment variable and will
incur API costs (~$5-10 for full suite).
"""

import asyncio
import json
import os

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
from tests.fixtures.response_storage import (
    save_response,
    validate_iam_policies,
    validate_mermaid_syntax,
    validate_response_structure,
)
from tests.test_scenarios.conftest import REPRESENTATIVE_COMBINATIONS, combination_id


# Skip all tests in this module if no API key is set
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.environ.get("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set - skipping integration tests",
    ),
]


class TestRealAPIIntegration:
    """
    Integration tests that call the real Claude API.

    These tests use the representative subset (24 combinations) to validate
    that real Claude responses meet our schema requirements.
    """

    @pytest.mark.parametrize(
        "combination",
        REPRESENTATIVE_COMBINATIONS,
        ids=[combination_id(c) for c in REPRESENTATIVE_COMBINATIONS],
    )
    @pytest.mark.asyncio
    async def test_real_api_response_is_valid(self, combination):
        """
        Test that real API responses parse correctly and have valid structure.
        """
        use_case, platform, pattern, classification, scale = combination

        from app.services.generator import ArchitectureGenerator

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        generator = ArchitectureGenerator(api_key)

        request = ArchitectureRequest(
            use_case=use_case,
            cloud_platform=platform,
            integration_pattern=pattern,
            data_classification=classification,
            scale_tier=scale,
        )

        # Call real API
        try:
            response = await generator.generate(request)
            response_dict = response.model_dump(by_alias=True)

            # Validate response structure
            structure_errors = validate_response_structure(response_dict)

            # Save response for debugging
            error_msg = "; ".join(structure_errors) if structure_errors else None
            save_response(
                response_dict,
                use_case,
                platform,
                pattern,
                classification,
                scale,
                error=error_msg,
            )

            # Assert no structure errors
            assert not structure_errors, f"Structure validation failed: {structure_errors}"

            # Validate we got a proper response object
            assert isinstance(response, ArchitectureResponse)
            assert response.architecture is not None
            assert response.compliance is not None
            assert response.deployment is not None
            assert response.sample_code is not None

        except Exception as e:
            # Save failed response for debugging
            save_response(
                {"error": str(e), "type": type(e).__name__},
                use_case,
                platform,
                pattern,
                classification,
                scale,
                error=str(e),
            )
            raise

    @pytest.mark.parametrize(
        "combination",
        REPRESENTATIVE_COMBINATIONS,
        ids=[combination_id(c) for c in REPRESENTATIVE_COMBINATIONS],
    )
    @pytest.mark.asyncio
    async def test_real_api_mermaid_syntax(self, combination):
        """
        Test that real API Mermaid diagrams have valid syntax.
        """
        use_case, platform, pattern, classification, scale = combination

        from app.services.generator import ArchitectureGenerator

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        generator = ArchitectureGenerator(api_key)

        request = ArchitectureRequest(
            use_case=use_case,
            cloud_platform=platform,
            integration_pattern=pattern,
            data_classification=classification,
            scale_tier=scale,
        )

        response = await generator.generate(request)
        diagram = response.architecture.mermaid_diagram

        # Validate Mermaid syntax
        mermaid_errors = validate_mermaid_syntax(diagram)

        if mermaid_errors:
            # Save response with errors for debugging
            response_dict = response.model_dump(by_alias=True)
            save_response(
                response_dict,
                use_case,
                platform,
                pattern,
                classification,
                scale,
                error=f"Mermaid errors: {'; '.join(mermaid_errors)}",
            )

        assert not mermaid_errors, f"Mermaid validation failed: {mermaid_errors}"

    @pytest.mark.parametrize(
        "combination",
        REPRESENTATIVE_COMBINATIONS,
        ids=[combination_id(c) for c in REPRESENTATIVE_COMBINATIONS],
    )
    @pytest.mark.asyncio
    async def test_real_api_iam_policies(self, combination):
        """
        Test that real API IAM policies are valid JSON with correct structure.
        """
        use_case, platform, pattern, classification, scale = combination

        from app.services.generator import ArchitectureGenerator

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        generator = ArchitectureGenerator(api_key)

        request = ArchitectureRequest(
            use_case=use_case,
            cloud_platform=platform,
            integration_pattern=pattern,
            data_classification=classification,
            scale_tier=scale,
        )

        response = await generator.generate(request)
        iam_policies = response.deployment.iam_policies

        # Validate IAM policies
        iam_errors = validate_iam_policies(iam_policies, platform)

        if iam_errors:
            # Save response with errors for debugging
            response_dict = response.model_dump(by_alias=True)
            save_response(
                response_dict,
                use_case,
                platform,
                pattern,
                classification,
                scale,
                error=f"IAM errors: {'; '.join(iam_errors)}",
            )

        assert not iam_errors, f"IAM validation failed: {iam_errors}"

    @pytest.mark.parametrize(
        "combination",
        REPRESENTATIVE_COMBINATIONS,
        ids=[combination_id(c) for c in REPRESENTATIVE_COMBINATIONS],
    )
    @pytest.mark.asyncio
    async def test_real_api_json_serialization(self, combination):
        """
        Test that real API responses serialize to valid JSON.
        """
        use_case, platform, pattern, classification, scale = combination

        from app.services.generator import ArchitectureGenerator

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        generator = ArchitectureGenerator(api_key)

        request = ArchitectureRequest(
            use_case=use_case,
            cloud_platform=platform,
            integration_pattern=pattern,
            data_classification=classification,
            scale_tier=scale,
        )

        response = await generator.generate(request)

        # Convert to dict and serialize to JSON
        response_dict = response.model_dump(by_alias=True)
        json_str = json.dumps(response_dict)

        # Parse back and verify
        parsed = json.loads(json_str)

        assert parsed == response_dict, "JSON serialization round-trip failed"

        # Verify camelCase aliases
        assert "sampleCode" in parsed
        assert "mermaidDiagram" in parsed["architecture"]
        assert "dataFlows" in parsed["architecture"]
        assert "baaRequirements" in parsed["compliance"]
        assert "iamPolicies" in parsed["deployment"]


class TestRealAPICloudPlatformContent:
    """
    Integration tests that validate cloud-specific content in real responses.
    """

    @pytest.mark.parametrize("use_case", list(UseCase))
    @pytest.mark.asyncio
    async def test_aws_responses_contain_aws_services(self, use_case):
        """
        Test that AWS platform responses mention AWS-specific services.
        """
        from app.services.generator import ArchitectureGenerator

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        generator = ArchitectureGenerator(api_key)

        request = ArchitectureRequest(
            use_case=use_case,
            cloud_platform=CloudPlatform.AWS_BEDROCK,
            integration_pattern=IntegrationPattern.API_GATEWAY,
            data_classification=DataClassification.PHI,
            scale_tier=ScaleTier.PRODUCTION,
        )

        response = await generator.generate(request)

        # Check components mention AWS services
        all_services = [c.service.lower() for c in response.architecture.components]
        services_str = " ".join(all_services)

        aws_keywords = ["aws", "amazon", "bedrock", "lambda", "s3", "dynamodb", "sqs"]
        has_aws_service = any(kw in services_str for kw in aws_keywords)

        assert has_aws_service, f"AWS response should mention AWS services, got: {all_services}"

    @pytest.mark.parametrize("use_case", list(UseCase))
    @pytest.mark.asyncio
    async def test_gcp_responses_contain_gcp_services(self, use_case):
        """
        Test that GCP platform responses mention GCP-specific services.
        """
        from app.services.generator import ArchitectureGenerator

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        generator = ArchitectureGenerator(api_key)

        request = ArchitectureRequest(
            use_case=use_case,
            cloud_platform=CloudPlatform.GCP_VERTEX,
            integration_pattern=IntegrationPattern.API_GATEWAY,
            data_classification=DataClassification.PHI,
            scale_tier=ScaleTier.PRODUCTION,
        )

        response = await generator.generate(request)

        # Check components mention GCP services
        all_services = [c.service.lower() for c in response.architecture.components]
        services_str = " ".join(all_services)

        gcp_keywords = ["cloud", "gcp", "google", "vertex", "firestore", "pub/sub"]
        has_gcp_service = any(kw in services_str for kw in gcp_keywords)

        assert has_gcp_service, f"GCP response should mention GCP services, got: {all_services}"


class TestRealAPIPHIHandling:
    """
    Integration tests that validate PHI handling in real responses.
    """

    @pytest.mark.parametrize("use_case", list(UseCase))
    @pytest.mark.asyncio
    async def test_phi_classification_has_phi_touchpoints(self, use_case):
        """
        Test that PHI data classification results in PHI touchpoints.
        """
        from app.services.generator import ArchitectureGenerator

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        generator = ArchitectureGenerator(api_key)

        request = ArchitectureRequest(
            use_case=use_case,
            cloud_platform=CloudPlatform.AWS_BEDROCK,
            integration_pattern=IntegrationPattern.API_GATEWAY,
            data_classification=DataClassification.PHI,
            scale_tier=ScaleTier.PRODUCTION,
        )

        response = await generator.generate(request)

        # PHI classification should have some components marked as PHI touchpoints
        phi_touchpoints = [c for c in response.architecture.components if c.phi_touchpoint]

        assert len(phi_touchpoints) > 0, (
            f"PHI data classification should have PHI touchpoints for {use_case}. "
            f"Components: {[c.name for c in response.architecture.components]}"
        )

    @pytest.mark.parametrize("use_case", list(UseCase))
    @pytest.mark.asyncio
    async def test_phi_classification_has_encryption_requirements(self, use_case):
        """
        Test that PHI data classification includes encryption requirements.
        """
        from app.services.generator import ArchitectureGenerator

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        generator = ArchitectureGenerator(api_key)

        request = ArchitectureRequest(
            use_case=use_case,
            cloud_platform=CloudPlatform.AWS_BEDROCK,
            integration_pattern=IntegrationPattern.API_GATEWAY,
            data_classification=DataClassification.PHI,
            scale_tier=ScaleTier.PRODUCTION,
        )

        response = await generator.generate(request)

        # Check compliance checklist mentions encryption
        checklist_text = " ".join(
            [item.requirement.lower() + " " + item.implementation.lower() for item in response.compliance.checklist]
        )

        encryption_keywords = ["encrypt", "kms", "tls", "ssl"]
        has_encryption = any(kw in checklist_text for kw in encryption_keywords)

        assert has_encryption, (
            f"PHI compliance should mention encryption. "
            f"Checklist: {[item.requirement for item in response.compliance.checklist]}"
        )
