"""
API Endpoint Tests for the Project Delay Risk AI FastAPI Application.

Tests all API endpoints including:
- Health check
- Risk analysis
- Cache management
"""

import pytest
from fastapi.testclient import TestClient

from backend.app import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_check_returns_ok(self, client):
        """Tests that health check returns OK status."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_root_endpoint(self, client):
        """Tests the root endpoint returns API info."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data


class TestAnalyzeEndpoint:
    """Tests for the /analyze endpoint."""

    def test_analyze_without_what_if(self, client):
        """Tests basic analysis without what-if scenario."""
        response = client.post("/analyze", json={"what_if": None})
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)
        assert len(data["results"]) > 0
        
        # Check first result structure
        first_result = data["results"][0]
        assert "task_id" in first_result
        assert "risk_level" in first_result
        assert first_result["risk_level"] in ["High", "Medium", "Low"]
        assert "risk_score" in first_result
        assert 0 <= first_result["risk_score"] <= 100
        assert "delay_probability" in first_result
        assert 0 <= first_result["delay_probability"] <= 1
        assert "reasons" in first_result
        assert "recommended_actions" in first_result

    def test_analyze_with_what_if(self, client):
        """Tests analysis with what-if scenario."""
        response = client.post("/analyze", json={"what_if": "add_resource"})
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        
        # At least some results should have what_if_impact
        has_what_if = any(
            r.get("what_if_impact") is not None 
            for r in data["results"]
        )
        assert has_what_if
        
        # Check what-if structure
        for result in data["results"]:
            if result.get("what_if_impact"):
                impact = result["what_if_impact"]
                assert "new_delay_probability" in impact
                assert "probability_reduction" in impact
                assert "scenario" in impact

    def test_analyze_all_scenarios(self, client):
        """Tests all what-if scenarios."""
        scenarios = ["add_resource", "reduce_dependencies", "improve_process"]
        
        for scenario in scenarios:
            response = client.post("/analyze", json={"what_if": scenario})
            assert response.status_code == 200


class TestAnalyzeRefreshEndpoint:
    """Tests for the /analyze/refresh endpoint."""

    def test_refresh_clears_cache(self, client):
        """Tests that refresh endpoint works."""
        response = client.post("/analyze/refresh", json={"what_if": None})
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data


class TestCacheEndpoint:
    """Tests for the /cache endpoint."""

    def test_clear_cache(self, client):
        """Tests clearing the cache."""
        response = client.delete("/cache")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cache_cleared"


class TestErrorHandling:
    """Tests for error handling."""

    def test_invalid_json(self, client):
        """Tests handling of invalid JSON."""
        response = client.post(
            "/analyze",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Validation error
