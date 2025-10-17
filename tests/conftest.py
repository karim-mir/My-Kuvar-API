import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ПЕРЕОПРЕДЕЛЯЕМ настройки для тестов
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.main import app
from app.database import get_db, Base
from app.models import User

# Тестовая база данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Фикстура для тестовой сессии базы данных"""
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Фикстура для тестового клиента FastAPI"""

    # Переопределяем зависимость базы данных
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Фикстура для тестового пользователя"""
    from app.auth import get_password_hash

    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "pass123"  # ← Укоротили пароль
    }

    # Создаем пользователя в базе
    hashed_password = get_password_hash(user_data["password"])
    user = User(
        email=user_data["email"],
        username=user_data["username"],
        password_hash=hashed_password
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture
def test_user_2(db_session):
    """Фикстура для второго тестового пользователя"""
    from app.auth import get_password_hash

    user_data = {
        "email": "test2@example.com",
        "username": "testuser2",
        "password": "pass456"  # ← Укоротили пароль
    }

    hashed_password = get_password_hash(user_data["password"])
    user = User(
        email=user_data["email"],
        username=user_data["username"],
        password_hash=hashed_password
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture
def auth_headers(test_user):
    """Фикстура для заголовков авторизации"""
    from app.auth import create_access_token

    token_data = {"sub": str(test_user.id)}
    access_token = create_access_token(token_data)

    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(autouse=True)
def cleanup_db(db_session):
    """Автоматическая очистка базы после каждого теста"""
    yield
    # Очищаем все таблицы
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()


@pytest.fixture
def mock_credentials():
    """Фикстура для мока credentials"""
    from unittest.mock import Mock
    from fastapi.security import HTTPAuthorizationCredentials

    def _create_mock_credentials(token: str):
        mock_creds = Mock(spec=HTTPAuthorizationCredentials)
        mock_creds.credentials = token
        return mock_creds

    return _create_mock_credentials
