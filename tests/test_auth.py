import pytest
from fastapi import status
from app.auth import create_access_token, verify_password, get_password_hash


class TestAuth:
    def test_password_hashing(self):
        """Тест хеширования пароля"""
        password = "testpassword"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) == True
        assert verify_password("wrongpassword", hashed) == False

    def test_token_creation(self):
        """Тест создания JWT токена"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0


class TestAuthEndpoints:
    def test_register_success(self, client, db_session):
        """Тест успешной регистрации пользователя"""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpassword123"
        }

        response = client.post("/register", json=user_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data  # Пароль не должен возвращаться

    def test_register_duplicate_email(self, client, db_session):
        """Тест регистрации с существующим email"""
        user_data = {
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "password123"
        }

        # Первая регистрация
        client.post("/register", json=user_data)

        # Вторая регистрация с тем же email
        duplicate_data = {
            "email": "duplicate@example.com",
            "username": "user2",
            "password": "password456"
        }

        response = client.post("/register", json=duplicate_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_success(self, client, db_session):
        """Тест успешного входа"""
        # Сначала регистрируем пользователя
        user_data = {
            "email": "login@example.com",
            "username": "loginuser",
            "password": "loginpassword123"
        }
        client.post("/register", json=user_data)

        # Пытаемся войти
        login_data = {
            "email": "login@example.com",
            "password": "loginpassword123"
        }

        response = client.post("/login", json=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, db_session):
        """Тест входа с неправильным паролем"""
        user_data = {
            "email": "wrongpass@example.com",
            "username": "wrongpassuser",
            "password": "correctpassword"
        }
        client.post("/register", json=user_data)

        login_data = {
            "email": "wrongpass@example.com",
            "password": "wrongpassword"
        }

        response = client.post("/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_me_unauthorized(self, client):
        """Тест доступа к /me без авторизации"""
        response = client.get("/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_me_authorized(self, client, db_session):
        """Тест доступа к /me с авторизацией"""
        # Регистрация и вход
        user_data = {
            "email": "me@example.com",
            "username": "meuser",
            "password": "mepassword123"
        }
        client.post("/register", json=user_data)

        login_data = {
            "email": "me@example.com",
            "password": "mepassword123"
        }
        login_response = client.post("/login", json=login_data)
        token = login_response.json()["access_token"]

        # Запрос с токеном
        response = client.get(
            "/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
