# My Kuvar REST API 🍳

[![FastAPI](https://img.shields.io/badge/FastAPI-0.119.0-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![Poetry](https://img.shields.io/badge/Poetry-1.8.0-60A5FA?logo=poetry)](https://python-poetry.org)

REST API с системой аутентификации пользователей.

## 🚀 Возможности

- **🔐 Аутентификация** - JWT токены для безопасного доступа
- **👥 Управление пользователями** - регистрация, авторизация, профили
- **📝 CRUD операции** - создание, чтение, обновление, удаление рецептов
- **🗄️ База данных** - PostgreSQL с SQLAlchemy ORM
- **📚 Автодокументация** - автоматическая генерация Swagger документации
- **🧪 Полное тестирование** - 92% покрытие кода тестами

## 🛠 Технологии

- **FastAPI** - современный, быстрый веб-фреймворк
- **SQLAlchemy** - ORM для работы с базой данных
- **PostgreSQL** - реляционная база данных
- **JWT** - JSON Web Tokens для аутентификации
- **Pydantic** - валидация данных и сериализация
- **Poetry** - управление зависимостями
- **Pytest** - фреймворк для тестирования
- **Pytest-cov** - измерение покрытия кода тестами

## 📦 Установка и запуск

### Предварительные требования

- Python 3.12+
- Poetry
- PostgreSQL

### 1. Клонирование репозитория

```
git clone <https://github.com/karim-mir/My-Kuvar-API>
cd "My Kuvar №1 (REST API)"
```

### 2. Настройка окружения
Создайте файл .env на основе .env.sample:

```commandline
cp .env.sample .env
```

Отредактируйте .env файл:
```commandline
DATABASE_URL=postgresql://username:password@localhost:5432/kuvar_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Установка зависимостей
```commandline
poetry install
```

### 4. Активация виртуального окружения
```commandline
poetry shell
```

### 5. Запуск приложения
```commandline
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Приложение будет доступно по адресу: http://localhost:8000

## 🧪 Тестирование
Проект имеет комплексную систему тестирования с покрытием 92% кода.

### Запуск тестов
```commandline
# Все тесты с отчетом о покрытии
pytest --cov=app --cov-report=term-missing

# С HTML отчетом
pytest --cov=app --cov-report=html

# Конкретная категория тестов
pytest -m "auth"
```

## Структура тестов
```
tests/
├── test_main.py              # Интеграционные тесты API endpoints
├── test_auth.py              # Тесты аутентификации
├── test_models_schemas.py    # Тесты моделей и схем
└── conftest.py               # Фикстуры и конфигурация
```

## Покрытие кода
```
Модуль	Покрытие	Статус
auth.py	94%	        ✅
config.py	100%	✅
models.py	100%	✅
schemas.py	94%	✅
database.py	100%	✅
Общее	        96%	✅
```
## Типы тестов
- Unit-тесты - тестирование отдельных функций и классов
- Интеграционные тесты - тестирование API endpoints
- Тесты аутентификации - полный цикл регистрации, логина, доступа
- Тесты валидации - проверка схем и моделей данных

## Примеры тестируемых сценариев

```
# Тестирование регистрации
def test_register_success(client, db_session):
    user_data = {
        "email": "test@example.com",
        "username": "testuser", 
        "password": "pass123"
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 200

# Тестирование аутентификации
def test_login_success(client, test_user):
    login_data = {
        "email": test_user.email,
        "password": "pass123"
    }
    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
```

## 📚 Документация API
После запуска приложения доступна автоматическая документация:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

## 🎯 Основные endpoints
#### Аутентификация
```commandline
Метод	Endpoint	Описание
POST	/register	Регистрация нового пользователя
POST	/login	        Авторизация и получение токена
GET	/me	        Информация о текущем пользователе
POST	/logout	        Выход из системы
```
#### Пример запроса регистрации
```commandline
curl -X POST "http://localhost:8000/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "username": "chef123",
       "password": "securepassword"
     }'
```
#### Пример запроса авторизации
```commandline
curl -X POST "http://localhost:8000/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "securepassword"
     }'
```
## 🗄️ Структура проекта
```commandline
My Kuvar API/
├── app/
│   ├── __init__.py
│   ├── main.py              # Основное приложение FastAPI
│   ├── auth.py              # Логика аутентификации
│   ├── models.py            # SQLAlchemy модели
│   ├── schemas.py           # Pydantic схемы
│   ├── database.py          # Настройка базы данных
│   └── config.py            # Конфигурация приложения
├── tests/                   # Тесты
│   ├── test_main.py
│   ├── test_auth.py
│   ├── test_models_schemas.py
│   └── conftest.py
├── .env.sample              # Пример переменных окружения
├── pyproject.toml           # Зависимости Poetry
├── poetry.lock              # Lock-файл зависимостей
└── README.md                # Документация
```

## 🔧 Разработка
#### Запуск в режиме разработки
```commandline
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
#### Проверка кода
```
poetry run flake8 app/
```
#### Активация виртуального окружения
```commandline
poetry shell
```

👨‍💻 Автор
Jalil Karimov

Email: karimov.jalil@mail.ru

GitHub: [https://github.com/karim-mir]