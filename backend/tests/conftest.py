"""
Pytest configuration and fixtures for GSI Architecture Generator tests.
"""

import os
import pytest
from unittest.mock import MagicMock, patch


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
