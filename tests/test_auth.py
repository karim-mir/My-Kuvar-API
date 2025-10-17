import pytest
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status
from unittest.mock import Mock

from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_user_by_email,
    authenticate_user,
    get_current_user
)
from app.config import settings


class TestPasswordFunctions:
    """Тесты для функций работы с паролями"""

    def test_verify_password_correct(self):
        """Тест проверки правильного пароля"""
        password = "pass123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) == True

    def test_verify_password_incorrect(self):
        """Тест проверки неправильного пароля"""
        password = "pass123"
        wrong_password = "wrong123"
        hashed = get_password_hash(password)
        assert verify_password(wrong_password, hashed) == False

    def test_get_password_hash_too_long(self):
        """Тест хеширования слишком длинного пароля"""
        long_password = "a" * 100
        with pytest.raises(ValueError, match="Password too long"):
            get_password_hash(long_password)


class TestTokenFunctions:
    """Тесты для функций работы с JWT токенами"""

    def test_create_access_token(self):
        """Тест создания access token"""
        data = {"sub": "123", "email": "test@example.com"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

        # Проверяем, что токен можно декодировать
        decoded = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        assert decoded["sub"] == "123"
        assert "exp" in decoded

    def test_create_access_token_expiration(self):
        """Тест срока действия токена"""
        data = {"sub": "123"}
        token = create_access_token(data)

        decoded = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Проверяем, что expiration установлен
        assert "exp" in decoded
        exp_time = datetime.fromtimestamp(decoded["exp"])
        assert exp_time > datetime.utcnow()


class TestUserFunctions:
    """Тесты для функций работы с пользователями"""

    def test_get_user_by_email_found(self, db_session, test_user):
        """Тест поиска пользователя по email (найден)"""
        found_user = get_user_by_email(db_session, test_user.email)
        assert found_user is not None
        assert found_user.email == test_user.email
        assert found_user.username == test_user.username

    def test_get_user_by_email_not_found(self, db_session):
        """Тест поиска пользователя по email (не найден)"""
        user = get_user_by_email(db_session, "nonexistent@example.com")
        assert user is None

    def test_authenticate_user_success(self, db_session, test_user):
        """Тест успешной аутентификации пользователя"""
        authenticated_user = authenticate_user(
            db_session,
            test_user.email,
            "pass123"  # Пароль из фикстуры test_user
        )
        assert authenticated_user is not None
        assert authenticated_user.email == test_user.email

    def test_authenticate_user_wrong_password(self, db_session, test_user):
        """Тест аутентификации с неправильным паролем"""
        authenticated_user = authenticate_user(
            db_session,
            test_user.email,
            "wrongpassword"
        )
        assert authenticated_user is False

    def test_authenticate_user_nonexistent(self, db_session):
        """Тест аутентификации несуществующего пользователя"""
        authenticated_user = authenticate_user(
            db_session,
            "nonexistent@example.com",
            "anypassword"
        )
        assert authenticated_user is False


class TestGetCurrentUser:
    """Тесты для функции get_current_user"""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, db_session, test_user, mock_credentials):
        """Тест успешного получения текущего пользователя"""
        token_data = {"sub": str(test_user.id)}
        valid_token = create_access_token(token_data)

        current_user = await get_current_user(
            credentials=mock_credentials(valid_token),
            db=db_session
        )

        assert current_user is not None
        assert current_user.id == test_user.id
        assert current_user.email == test_user.email

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, db_session, mock_credentials):
        """Тест с невалидным токеном"""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                credentials=mock_credentials("invalid.token.here"),
                db=db_session
            )

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_current_user_nonexistent_user(self, db_session, mock_credentials):
        """Тест с токеном для несуществующего пользователя"""
        # Создаем токен для несуществующего ID
        token_data = {"sub": "999999"}
        token = create_access_token(token_data)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                credentials=mock_credentials(token),
                db=db_session
            )

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


# Простые тесты для быстрой проверки
def test_basic_functionality():
    """Базовый тест работы хеширования"""
    password = "test123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) == True
    assert verify_password("wrong", hashed) == False
