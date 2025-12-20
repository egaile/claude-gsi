"""
Tests for Pydantic models.
"""

import pytest
from pydantic import ValidationError

from app.models import (
    ArchitectureRequest,
    ArchitectureResponse,
    UseCase,
    CloudPlatform,
    IntegrationPattern,
    DataClassification,
    ScaleTier,
)


class TestArchitectureRequest:
    """Tests for the ArchitectureRequest model."""

    def test_valid_request_with_snake_case(self):
        """Should accept valid request with snake_case field names."""
        request = ArchitectureRequest(
            use_case=UseCase.CLINICAL_DOCUMENTATION,
            cloud_platform=CloudPlatform.AWS_BEDROCK,
            integration_pattern=IntegrationPattern.API_GATEWAY,
            data_classification=DataClassification.PHI,
            scale_tier=ScaleTier.PRODUCTION
        )
        assert request.use_case == UseCase.CLINICAL_DOCUMENTATION

    def test_valid_request_with_camel_case(self):
        """Should accept valid request with camelCase field names (alias)."""
        request = ArchitectureRequest(
            useCase="clinical-documentation",
            cloudPlatform="aws-bedrock",
            integrationPattern="api-gateway",
            dataClassification="phi",
            scaleTier="production"
        )
        assert request.use_case == UseCase.CLINICAL_DOCUMENTATION

    def test_invalid_use_case_rejected(self):
        """Should reject invalid use case values."""
        with pytest.raises(ValidationError):
            ArchitectureRequest(
                use_case="invalid-use-case",
                cloud_platform=CloudPlatform.AWS_BEDROCK,
                integration_pattern=IntegrationPattern.API_GATEWAY,
                data_classification=DataClassification.PHI,
                scale_tier=ScaleTier.PRODUCTION
            )

    def test_all_use_cases_valid(self):
        """All defined use cases should be valid."""
        for use_case in UseCase:
            request = ArchitectureRequest(
                use_case=use_case,
                cloud_platform=CloudPlatform.AWS_BEDROCK,
                integration_pattern=IntegrationPattern.API_GATEWAY,
                data_classification=DataClassification.PHI,
                scale_tier=ScaleTier.PRODUCTION
            )
            assert request.use_case == use_case

    def test_all_cloud_platforms_valid(self):
        """All defined cloud platforms should be valid."""
        for platform in CloudPlatform:
            request = ArchitectureRequest(
                use_case=UseCase.CLINICAL_DOCUMENTATION,
                cloud_platform=platform,
                integration_pattern=IntegrationPattern.API_GATEWAY,
                data_classification=DataClassification.PHI,
                scale_tier=ScaleTier.PRODUCTION
            )
            assert request.cloud_platform == platform


class TestArchitectureResponse:
    """Tests for the ArchitectureResponse model."""

    def test_valid_response_parsing(self, sample_architecture_response):
        """Should parse valid response data."""
        response = ArchitectureResponse.model_validate(sample_architecture_response)
        assert response.architecture is not None
        assert response.compliance is not None
        assert response.deployment is not None
        assert response.sample_code is not None

    def test_response_serializes_with_aliases(self, sample_architecture_response):
        """Response should serialize with camelCase aliases."""
        response = ArchitectureResponse.model_validate(sample_architecture_response)
        serialized = response.model_dump(by_alias=True)

        # Should use camelCase
        assert "sampleCode" in serialized
        assert "mermaidDiagram" in serialized["architecture"]

    def test_component_phi_touchpoint_parsing(self, sample_architecture_response):
        """Should correctly parse PHI touchpoint boolean."""
        response = ArchitectureResponse.model_validate(sample_architecture_response)
        component = response.architecture.components[0]
        assert isinstance(component.phi_touchpoint, bool)

    def test_data_flow_encryption_parsing(self, sample_architecture_response):
        """Should correctly parse encryption boolean."""
        response = ArchitectureResponse.model_validate(sample_architecture_response)
        data_flow = response.architecture.data_flows[0]
        assert isinstance(data_flow.encrypted, bool)
        assert data_flow.encrypted is True
