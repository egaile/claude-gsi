"""
Pytest configuration and fixtures for scenario combination tests.
"""

import json
from itertools import product
from unittest.mock import MagicMock

import pytest

from app.models import (
    ArchitectureRequest,
    CloudPlatform,
    DataClassification,
    IntegrationPattern,
    ScaleTier,
    UseCase,
)
from tests.fixtures.mock_responses import (
    generate_mock_architecture_response,
    generate_mock_code_response,
    generate_mock_streaming_response,
)


# All parameter values
USE_CASES = list(UseCase)
CLOUD_PLATFORMS = list(CloudPlatform)
INTEGRATION_PATTERNS = list(IntegrationPattern)
DATA_CLASSIFICATIONS = list(DataClassification)
SCALE_TIERS = list(ScaleTier)

# Generate all 288 combinations
ALL_COMBINATIONS = list(
    product(
        USE_CASES,
        CLOUD_PLATFORMS,
        INTEGRATION_PATTERNS,
        DATA_CLASSIFICATIONS,
        SCALE_TIERS,
    )
)

# Representative subset for integration tests (24 combinations)
# Uses PHI (most restrictive) and production (middle scale) for realistic testing
REPRESENTATIVE_COMBINATIONS = list(
    product(
        USE_CASES,
        CLOUD_PLATFORMS,
        INTEGRATION_PATTERNS,
        [DataClassification.PHI],
        [ScaleTier.PRODUCTION],
    )
)

# Code generation combinations (8 = 4 use cases × 2 platforms)
CODE_GEN_COMBINATIONS = list(product(USE_CASES, CLOUD_PLATFORMS))


def combination_id(combo: tuple) -> str:
    """Generate readable test ID for parametrized combination."""
    use_case, platform, pattern, classification, scale = combo
    return f"{use_case.value[:8]}-{platform.value[:3]}-{pattern.value[:3]}-{classification.value[:3]}-{scale.value[:4]}"


def code_gen_id(combo: tuple) -> str:
    """Generate test ID for code generation combinations."""
    use_case, platform = combo
    return f"{use_case.value}-{platform.value}"


@pytest.fixture
def mock_claude_response_factory():
    """
    Factory fixture that creates mock Anthropic message responses.
    """

    def _create_mock(
        use_case: UseCase,
        cloud_platform: CloudPlatform,
        integration_pattern: IntegrationPattern,
        data_classification: DataClassification,
        scale_tier: ScaleTier,
        include_sample_code: bool = True,
    ) -> MagicMock:
        if include_sample_code:
            response_data = generate_mock_architecture_response(
                use_case,
                cloud_platform,
                integration_pattern,
                data_classification,
                scale_tier,
            )
        else:
            response_data = generate_mock_streaming_response(
                use_case,
                cloud_platform,
                integration_pattern,
                data_classification,
                scale_tier,
            )

        mock_message = MagicMock()
        mock_message.stop_reason = "end_turn"
        mock_message.content = [MagicMock(text=json.dumps(response_data))]
        return mock_message

    return _create_mock


@pytest.fixture
def mock_code_response_factory():
    """
    Factory fixture for code generation responses.
    """

    def _create_mock(
        use_case: UseCase,
        cloud_platform: CloudPlatform,
    ) -> MagicMock:
        response_data = generate_mock_code_response(use_case, cloud_platform)

        mock_message = MagicMock()
        mock_message.stop_reason = "end_turn"
        mock_message.content = [MagicMock(text=json.dumps(response_data))]
        return mock_message

    return _create_mock


@pytest.fixture
def architecture_request_factory():
    """Factory to create ArchitectureRequest objects from combination tuples."""

    def _create(combo: tuple) -> ArchitectureRequest:
        use_case, platform, pattern, classification, scale = combo
        return ArchitectureRequest(
            use_case=use_case,
            cloud_platform=platform,
            integration_pattern=pattern,
            data_classification=classification,
            scale_tier=scale,
        )

    return _create


class MockStreamContext:
    """Mock context manager for Anthropic streaming responses."""

    def __init__(self, response_text: str, chunk_size: int = 200):
        self.response_text = response_text
        self.chunk_size = chunk_size

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    @property
    def text_stream(self):
        """Yield response in chunks to simulate streaming."""
        for i in range(0, len(self.response_text), self.chunk_size):
            yield self.response_text[i : i + self.chunk_size]


@pytest.fixture
def mock_stream_context_factory():
    """
    Factory fixture for creating streaming context managers.
    """

    def _create(
        use_case: UseCase,
        cloud_platform: CloudPlatform,
        integration_pattern: IntegrationPattern,
        data_classification: DataClassification,
        scale_tier: ScaleTier,
    ) -> MockStreamContext:
        response_data = generate_mock_streaming_response(
            use_case,
            cloud_platform,
            integration_pattern,
            data_classification,
            scale_tier,
        )
        return MockStreamContext(json.dumps(response_data))

    return _create
