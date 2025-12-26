"""
Pytest configuration and fixtures for GSI Architecture Generator tests.
"""

import json
import os
from itertools import product
from unittest.mock import MagicMock, patch

import pytest

from app.models import (
    CloudPlatform,
    DataClassification,
    IntegrationPattern,
    ScaleTier,
    UseCase,
)


# Register markers
def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests that call real APIs (deselect with '-m \"not integration\"')"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


# Combination helpers for parametrized tests
ALL_USE_CASES = list(UseCase)
ALL_CLOUD_PLATFORMS = list(CloudPlatform)
ALL_INTEGRATION_PATTERNS = list(IntegrationPattern)
ALL_DATA_CLASSIFICATIONS = list(DataClassification)
ALL_SCALE_TIERS = list(ScaleTier)

# All 288 combinations
ALL_SCENARIO_COMBINATIONS = list(
    product(
        ALL_USE_CASES,
        ALL_CLOUD_PLATFORMS,
        ALL_INTEGRATION_PATTERNS,
        ALL_DATA_CLASSIFICATIONS,
        ALL_SCALE_TIERS,
    )
)


@pytest.fixture
def mock_anthropic_client():
    """Create a mock Anthropic client for testing."""
    with patch('anthropic.Anthropic') as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def sample_architecture_response():
    """Sample valid architecture response from Claude."""
    return {
        "architecture": {
            "mermaidDiagram": "flowchart TD\n    A[Client] --> B[API Gateway]",
            "components": [
                {
                    "name": "API Gateway",
                    "service": "AWS API Gateway",
                    "purpose": "Entry point for requests",
                    "phiTouchpoint": False
                }
            ],
            "dataFlows": [
                {
                    "from": "Client",
                    "to": "API Gateway",
                    "data": "Request",
                    "encrypted": True
                }
            ]
        },
        "compliance": {
            "checklist": [
                {
                    "category": "technical",
                    "requirement": "Encryption at rest",
                    "implementation": "Use KMS",
                    "priority": "required"
                }
            ],
            "baaRequirements": "Sign BAA with AWS"
        },
        "deployment": {
            "steps": ["Step 1", "Step 2"],
            "iamPolicies": ["policy-1"],
            "networkConfig": "VPC setup",
            "monitoringSetup": "CloudWatch"
        },
        "sampleCode": {
            "python": "# Python code",
            "typescript": "// TypeScript code"
        }
    }


@pytest.fixture
def env_with_api_key():
    """Set up environment with valid API key."""
    original = os.environ.get("ANTHROPIC_API_KEY")
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-api03-test-key-for-testing-purposes-only-do-not-use"
    yield
    if original:
        os.environ["ANTHROPIC_API_KEY"] = original
    else:
        os.environ.pop("ANTHROPIC_API_KEY", None)


# Import fixtures from test_scenarios for availability across all tests
# These are imported here so they're available to all test modules
try:
    from tests.fixtures.mock_responses import (
        generate_mock_architecture_response,
        generate_mock_code_response,
        generate_mock_streaming_response,
    )

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

except ImportError:
    # Fixtures not available if mock_responses module doesn't exist yet
    pass
