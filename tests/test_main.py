import pytest
from fastapi import status


class TestMainEndpoints:
    def test_root_endpoint(self, client):
        """Тест корневого endpoint"""
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data

    def test_health_check(self, client):
        """Тест health check endpoint (если есть)"""
        response = client.get("/health")

        # Если endpoint существует
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK

    def test_documentation_access(self, client):
        """Тест доступности документации"""
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK

        response = client.get("/redoc")
        assert response.status_code == status.HTTP_200_OK
