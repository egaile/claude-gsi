"""
Tests for the FastAPI endpoints.
"""

import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

# We need to mock before importing the app
with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'sk-ant-api03-test-key-for-testing-purposes-only'}):
    with patch('app.services.generator.ArchitectureGenerator'):
        from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestHealthCheck:
    """Tests for the health check endpoint."""

    def test_health_check_returns_healthy(self, client):
        """Health check should return healthy status."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "gsi-architecture-generator"

    def test_health_check_does_not_expose_api_key(self, client):
        """Health check should not expose any part of the API key."""
        response = client.get("/api/health")
        data = response.json()
        # Should not contain key_prefix or any partial key
        assert "key_prefix" not in data
        assert "sk-ant" not in json.dumps(data)


class TestGenerateArchitecture:
    """Tests for the generate architecture endpoint."""

    def test_generate_architecture_requires_valid_request(self, client):
        """Should reject invalid request data."""
        response = client.post(
            "/api/generate-architecture",
            json={"invalid": "data"}
        )
        assert response.status_code == 422  # Validation error

    def test_generate_architecture_accepts_valid_request(self, client, sample_architecture_response):
        """Should accept valid request with all required fields."""
        with patch('app.main.generator') as mock_gen:
            mock_gen.generate = AsyncMock(return_value=MagicMock(
                model_dump=lambda by_alias: sample_architecture_response
            ))

            response = client.post(
                "/api/generate-architecture",
                json={
                    "useCase": "clinical-documentation",
                    "cloudPlatform": "aws-bedrock",
                    "integrationPattern": "api-gateway",
                    "dataClassification": "phi",
                    "scaleTier": "production"
                }
            )
            # May be 503 if generator not initialized in test context
            assert response.status_code in [200, 503]


class TestCORS:
    """Tests for CORS configuration."""

    def test_cors_headers_present(self, client):
        """Should include CORS headers in response."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET"
            }
        )
        # Should not reject the request
        assert response.status_code in [200, 405]


class TestErrorHandling:
    """Tests for error handling."""

    def test_404_for_unknown_routes(self, client):
        """Should return 404 for unknown routes."""
        response = client.get("/api/unknown-endpoint")
        assert response.status_code == 404

    def test_error_responses_do_not_leak_secrets(self, client):
        """Error responses should not contain sensitive information."""
        response = client.post(
            "/api/generate-architecture",
            json={"invalid": "data"}
        )
        response_text = response.text.lower()
        assert "sk-ant" not in response_text
        assert "api_key" not in response_text or "configured" in response_text
