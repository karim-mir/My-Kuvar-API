# My Kuvar REST API 🍳

[![FastAPI](https://img.shields.io/badge/FastAPI-0.119.0-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![Poetry](https://img.shields.io/badge/Poetry-1.8.0-60A5FA?logo=poetry)](https://python-poetry.org)

REST API для управления кулинарными рецептами с системой аутентификации пользователей.

## 🚀 Возможности

- **🔐 Аутентификация** - JWT токены для безопасного доступа
- **👥 Управление пользователями** - регистрация, авторизация, профили
- **📝 CRUD операции** - создание, чтение, обновление, удаление рецептов
- **🗄️ База данных** - PostgreSQL с SQLAlchemy ORM
- **📚 Автодокументация** - автоматическая генерация Swagger документации

## 🛠 Технологии

- **FastAPI** - современный, быстрый веб-фреймворк
- **SQLAlchemy** - ORM для работы с базой данных
- **PostgreSQL** - реляционная база данных
- **JWT** - JSON Web Tokens для аутентификации
- **Pydantic** - валидация данных и сериализация
- **Poetry** - управление зависимостями

## 📦 Установка и запуск

### Предварительные требования

- Python 3.12+
- Poetry
- PostgreSQL

### 1. Клонирование репозитория

```
git clone <your-repository-url>
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

## 📚 Документация API
После запуска приложения доступна автоматическая документация:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

## 🎯 Основные endpoints
#### Аутентификация
```commandline
Метод	Endpoint	Описание
POST	/register	Регистрация нового пользователя
POST	/login	    Авторизация и получение токена
GET	    /me	        Информация о текущем пользователе
POST	/logout	    Выход из системы
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
My Kuvar №1 (REST API)/
├── app/
│   ├── __init__.py
│   ├── main.py              # Основное приложение FastAPI
│   ├── auth.py              # Логика аутентификации
│   ├── models.py            # SQLAlchemy модели
│   ├── schemas.py           # Pydantic схемы
│   ├── database.py          # Настройка базы данных
│   └── config.py            # Конфигурация приложения
├── .env.sample              # Пример переменных окружения
├── pyproject.toml           # Зависимости Poetry
├── poetry.lock              # Lock-файл зависимостей
└── manage.py                # Django management (если используется)
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

Email: karimov.nazir00@yandex.ru

GitHub: [https://github.com/karim-mir]