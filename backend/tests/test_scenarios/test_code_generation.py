"""
Tests for code generation endpoint with use case and platform combinations.
"""

import asyncio
import json
from unittest.mock import MagicMock

import pytest

from app.models import (
    CloudPlatform,
    CodeGenerationRequest,
    CodeGenerationResponse,
    UseCase,
)
from tests.fixtures.mock_responses import generate_mock_code_response
from tests.test_scenarios.conftest import CODE_GEN_COMBINATIONS, code_gen_id


class TestCodeGenerationResponseValidation:
    """Tests that validate code generation response format."""

    @pytest.mark.parametrize(
        "combination",
        CODE_GEN_COMBINATIONS,
        ids=[code_gen_id(c) for c in CODE_GEN_COMBINATIONS],
    )
    def test_code_response_parses_correctly(self, combination):
        """
        Validate that code generation responses parse correctly.
        """
        use_case, platform = combination

        mock_response_data = generate_mock_code_response(use_case, platform)

        # Verify sampleCode is present
        assert "sampleCode" in mock_response_data
        assert "python" in mock_response_data["sampleCode"]
        assert "typescript" in mock_response_data["sampleCode"]

        # Verify code is non-empty
        assert len(mock_response_data["sampleCode"]["python"]) > 0
        assert len(mock_response_data["sampleCode"]["typescript"]) > 0

    @pytest.mark.parametrize(
        "combination",
        CODE_GEN_COMBINATIONS,
        ids=[code_gen_id(c) for c in CODE_GEN_COMBINATIONS],
    )
    def test_code_response_parses_to_pydantic_model(self, combination):
        """
        Validate that code responses parse into Pydantic model.
        """
        use_case, platform = combination

        mock_response_data = generate_mock_code_response(use_case, platform)

        # Parse into model
        response = CodeGenerationResponse.model_validate(mock_response_data)

        assert response.sample_code is not None
        assert response.sample_code.python is not None
        assert response.sample_code.typescript is not None


class TestPythonCodeContent:
    """Tests that validate Python code content."""

    @pytest.mark.parametrize(
        "combination",
        CODE_GEN_COMBINATIONS,
        ids=[code_gen_id(c) for c in CODE_GEN_COMBINATIONS],
    )
    def test_python_code_has_imports(self, combination):
        """
        Validate that Python code includes necessary imports.
        """
        use_case, platform = combination

        mock_response_data = generate_mock_code_response(use_case, platform)
        python_code = mock_response_data["sampleCode"]["python"]

        assert "import" in python_code

    @pytest.mark.parametrize("use_case", list(UseCase))
    def test_aws_python_code_uses_boto3(self, use_case):
        """
        Validate that AWS Python code uses boto3.
        """
        mock_response_data = generate_mock_code_response(use_case, CloudPlatform.AWS_BEDROCK)
        python_code = mock_response_data["sampleCode"]["python"]

        assert "boto3" in python_code

    @pytest.mark.parametrize("use_case", list(UseCase))
    def test_gcp_python_code_uses_vertex(self, use_case):
        """
        Validate that GCP Python code uses Vertex AI.
        """
        mock_response_data = generate_mock_code_response(use_case, CloudPlatform.GCP_VERTEX)
        python_code = mock_response_data["sampleCode"]["python"]

        assert "vertexai" in python_code or "vertex" in python_code.lower()


class TestTypeScriptCodeContent:
    """Tests that validate TypeScript code content."""

    @pytest.mark.parametrize(
        "combination",
        CODE_GEN_COMBINATIONS,
        ids=[code_gen_id(c) for c in CODE_GEN_COMBINATIONS],
    )
    def test_typescript_code_has_imports(self, combination):
        """
        Validate that TypeScript code includes necessary imports.
        """
        use_case, platform = combination

        mock_response_data = generate_mock_code_response(use_case, platform)
        typescript_code = mock_response_data["sampleCode"]["typescript"]

        assert "import" in typescript_code

    @pytest.mark.parametrize("use_case", list(UseCase))
    def test_aws_typescript_code_uses_aws_sdk(self, use_case):
        """
        Validate that AWS TypeScript code uses AWS SDK.
        """
        mock_response_data = generate_mock_code_response(use_case, CloudPlatform.AWS_BEDROCK)
        typescript_code = mock_response_data["sampleCode"]["typescript"]

        assert "@aws-sdk" in typescript_code or "aws" in typescript_code.lower()

    @pytest.mark.parametrize("use_case", list(UseCase))
    def test_gcp_typescript_code_uses_google_cloud(self, use_case):
        """
        Validate that GCP TypeScript code uses Google Cloud SDK.
        """
        mock_response_data = generate_mock_code_response(use_case, CloudPlatform.GCP_VERTEX)
        typescript_code = mock_response_data["sampleCode"]["typescript"]

        assert "@google-cloud" in typescript_code or "vertexai" in typescript_code.lower()


class TestCodeGenerationWithMockedAPI:
    """Tests that exercise the code generator with mocked responses."""

    @pytest.mark.parametrize(
        "combination",
        CODE_GEN_COMBINATIONS,
        ids=[code_gen_id(c) for c in CODE_GEN_COMBINATIONS],
    )
    def test_code_generator_accepts_combination(
        self, combination, mock_anthropic_client, mock_code_response_factory
    ):
        """
        Validate code generation for each use case and platform combination.
        """
        use_case, platform = combination

        # Configure mock
        mock_response = mock_code_response_factory(use_case, platform)
        mock_anthropic_client.messages.create.return_value = mock_response

        from app.services.generator import ArchitectureGenerator

        generator = ArchitectureGenerator("sk-ant-api03-test-key")

        request = CodeGenerationRequest(
            use_case=use_case,
            cloud_platform=platform,
            architecture_summary="Test architecture summary for code generation",
        )

        response = asyncio.run(generator.generate_code(request))

        assert response is not None
        assert response.sample_code is not None
        assert response.sample_code.python is not None
        assert response.sample_code.typescript is not None

        # Verify code contains expected platform references
        if platform == CloudPlatform.AWS_BEDROCK:
            assert (
                "boto3" in response.sample_code.python
                or "aws" in response.sample_code.python.lower()
            )
            assert (
                "@aws-sdk" in response.sample_code.typescript
                or "aws" in response.sample_code.typescript.lower()
            )
        else:
            assert (
                "google" in response.sample_code.python.lower()
                or "vertex" in response.sample_code.python.lower()
            )
            assert (
                "@google-cloud" in response.sample_code.typescript
                or "vertex" in response.sample_code.typescript.lower()
            )
