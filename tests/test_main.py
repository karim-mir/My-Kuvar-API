import pytest
from fastapi import status
from jose import jwt

from app.config import settings
from app import schemas


class TestRegisterEndpoint:
    """Тесты для endpoint /register"""

    def test_register_success(self, client, db_session):
        """Тест успешной регистрации пользователя"""
        # Используем уникальные данные для каждого теста
        user_data = {
            "email": "unique_register@example.com",
            "username": "uniqueregisteruser",
            "password": "pass123"
        }

        response = client.post("/register", json=user_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data

    def test_register_duplicate_email(self, client, test_user):
        """Тест регистрации с существующим email"""
        duplicate_data = {
            "email": test_user.email,
            "username": "differentuser",
            "password": "differentpass"
        }

        response = client.post("/register", json=duplicate_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_data(self, client):
        """Тест регистрации с невалидными данными"""
        invalid_data = {
            "email": "invalid-email",
            "username": "user",
            "password": "pass"
        }

        response = client.post("/register", json=invalid_data)

        # Pydantic валидация может вернуть 422
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST]

    def test_register_missing_fields(self, client):
        """Тест регистрации с отсутствующими полями"""
        incomplete_data = {
            "email": "test@example.com"
            # Нет username и password
        }

        response = client.post("/register", json=incomplete_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLoginEndpoint:
    """Тесты для endpoint /login"""

    def test_login_success(self, client, test_user):
        """Тест успешного входа"""
        login_data = {
            "email": test_user.email,
            "password": "pass123"
        }

        response = client.post("/login", json=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # Проверяем, что токен валиден
        token = data["access_token"]
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        assert payload["sub"] == str(test_user.id)

    def test_login_wrong_password(self, client, test_user):
        """Тест входа с неправильным паролем"""
        login_data = {
            "email": test_user.email,
            "password": "wrongpassword"
        }

        response = client.post("/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client):
        """Тест входа несуществующего пользователя"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "anypassword"
        }

        response = client.post("/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_invalid_data(self, client):
        """Тест входа с невалидными данными"""
        invalid_data = {
            "email": "invalid-email",
            "password": "pass"
        }

        response = client.post("/login", json=invalid_data)

        # Может вернуть 401 (пользователь не найден) или 422 (валидация)
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestMeEndpoint:
    """Тесты для endpoint /me"""

    def test_get_me_success(self, client, auth_headers, test_user):
        """Тест успешного получения информации о текущем пользователе"""
        response = client.get("/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert "password" not in data

    def test_get_me_unauthorized(self, client):
        """Тест доступа к /me без авторизации"""
        response = client.get("/me")

        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_get_me_invalid_token(self, client):
        """Тест доступа к /me с невалидным токеном"""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_me_expired_token(self, client, expired_token_headers):
        """Тест доступа к /me с просроченным токеном"""
        response = client.get("/me", headers=expired_token_headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLogoutEndpoint:
    """Тесты для endpoint /logout"""

    def test_logout_success(self, client, test_user):
        """Тест успешного выхода из системы"""
        from app.auth import create_access_token

        # Создаем новый токен для этого теста
        token = create_access_token({"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        # Сначала токен работает
        response_before = client.get("/me", headers=headers)
        assert response_before.status_code == status.HTTP_200_OK

        # Выходим из системы
        response = client.post("/logout", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Successfully logged out"

        # Токен больше не должен работать - ловим исключение
        try:
            response_after = client.get("/me", headers=headers)
            # Если не выбросило исключение, проверяем статус
            assert response_after.status_code == status.HTTP_401_UNAUTHORIZED
            assert "invalidated" in response_after.json()["detail"].lower()
        except Exception as e:
            # Проверяем, что это правильное исключение
            assert "401" in str(e)
            assert "Token has been invalidated" in str(e)


class TestTokenBlacklist:
    """Тесты для черного списка токенов"""

    def test_blacklisted_token_rejected(self, client, test_user):
        """Тест, что токен из черного списка отклоняется"""
        from app.auth import create_access_token

        # Создаем токен
        token = create_access_token({"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        # Сначала токен работает
        response_before = client.get("/me", headers=headers)
        assert response_before.status_code == status.HTTP_200_OK

        # Добавляем токен в черный список через logout
        logout_response = client.post("/logout", headers=headers)
        assert logout_response.status_code == status.HTTP_200_OK

        # Теперь токен не должен работать - ловим исключение
        try:
            response_after = client.get("/me", headers=headers)
            # Если не выбросило исключение, проверяем статус
            assert response_after.status_code == status.HTTP_401_UNAUTHORIZED
            assert "invalidated" in response_after.json()["detail"].lower()
        except Exception as e:
            # Проверяем, что это правильное исключение
            assert "401" in str(e)
            assert "Token has been invalidated" in str(e)


class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_multiple_logins_create_different_tokens(self, client, test_user):
        """Тест, что multiple логины создают разные токены"""
        login_data = {
            "email": test_user.email,
            "password": "pass123"
        }

        # Первый логин
        response1 = client.post("/login", json=login_data)
        assert response1.status_code == status.HTTP_200_OK
        token1 = response1.json()["access_token"]

        # Второй логин
        response2 = client.post("/login", json=login_data)
        assert response2.status_code == status.HTTP_200_OK
        token2 = response2.json()["access_token"]

        # Токены должны быть разными (теперь с uuid в payload)
        assert token1 != token2

        # Оба токена должны работать
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}

        assert client.get("/me", headers=headers1).status_code == status.HTTP_200_OK
        assert client.get("/me", headers=headers2).status_code == status.HTTP_200_OK


class TestAPIStructure:
    """Тесты структуры API"""

    def test_api_documentation_accessible(self, client):
        """Тест доступности документации"""
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK

        response = client.get("/redoc")
        assert response.status_code == status.HTTP_200_OK

    def test_openapi_schema_accessible(self, client):
        """Тест доступности OpenAPI схемы"""
        response = client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
