import pytest
from pydantic import ValidationError
from app import schemas


class TestSchemas:
    def test_user_create_valid(self):
        """Тест валидных данных для создания пользователя"""
        valid_data = {
            "email": "valid@example.com",
            "username": "validuser",
            "password": "validpassword123"
        }

        user = schemas.UserCreate(**valid_data)

        assert user.email == valid_data["email"]
        assert user.username == valid_data["username"]
        assert user.password == valid_data["password"]

    def test_user_create_invalid_email(self):
        """Тест невалидного email"""
        invalid_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "password123"
        }

        with pytest.raises(ValidationError):
            schemas.UserCreate(**invalid_data)

    def test_user_response_structure(self):
        """Тест структуры ответа пользователя"""
        response_data = {
            "id": 1,
            "email": "response@example.com",
            "username": "responseuser",
            "created_at": "2024-01-15T10:30:00"
        }

        user_response = schemas.UserResponse(**response_data)

        assert user_response.id == response_data["id"]
        assert user_response.email == response_data["email"]
        assert user_response.username == response_data["username"]
        assert "password" not in user_response.dict()

    def test_token_schema(self):
        """Тест схемы токена"""
        token_data = {
            "access_token": "test_token_123",
            "token_type": "bearer"
        }

        token = schemas.Token(**token_data)

        assert token.access_token == token_data["access_token"]
        assert token.token_type == token_data["token_type"]
