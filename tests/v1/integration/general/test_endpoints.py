"""
This file contains the integration tests for the general endpoints
"""

from tests.v1.integration.utils.utils import execute_and_validate_endpoint
from app.api.v1.general.types import HealthCheckResponse, VersionResponse


def test_healthcheck() -> None:
    execute_and_validate_endpoint(
        "/api/v1/health", {}, HealthCheckResponse, method="GET"
    )


def test_version(monkeypatch) -> None:
    version = "1.0.0"
    monkeypatch.setenv("APP_VERSION", version)
    response = execute_and_validate_endpoint(
        "/api/v1/version", {}, VersionResponse, method="GET"
    )
    assert response.version == version
