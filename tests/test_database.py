import pytest
from sqlalchemy import text
from app.database import get_db, SessionLocal, engine


class TestDatabase:
    """Тесты для подключения к базе данных"""

    def test_database_connection(self, db_session):
        """Тест подключения к базе данных"""
        # Простой запрос для проверки соединения
        result = db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1

    def test_get_db_dependency(self):
        """Тест dependency get_db"""
        # Создаем генератор
        db_generator = get_db()

        # Получаем сессию
        db = next(db_generator)

        try:
            # Проверяем что это действительно сессия
            assert db is not None
            assert hasattr(db, 'execute')

            # Проверяем что сессия работает
            result = db.execute(text("SELECT 1"))
            assert result.scalar() == 1
        finally:
            # Важно: закрываем генератор чтобы покрыть finally блок
            try:
                next(db_generator)
            except StopIteration:
                pass  # Ожидаемое поведение

    def test_session_local(self):
        """Тест создания сессии"""
        session = SessionLocal()
        try:
            assert session is not None
            # Проверяем базовую функциональность
            result = session.execute(text("SELECT 1"))
            assert result.scalar() == 1
        finally:
            session.close()

    def test_engine_connection(self):
        """Тест подключения через engine"""
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            assert result.scalar() == 1
