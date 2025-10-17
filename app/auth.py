import uuid
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .config import settings
from .models import User
from .schemas import TokenData
from .database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширование пароля с проверкой длины для bcrypt"""
    if len(password.encode('utf-8')) > 72:
        raise ValueError("Password too long. Maximum length is 72 bytes.")
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),  # время создания
        "jti": str(uuid.uuid4())  # уникальный идентификатор
    })

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return False
    return user


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        print(f"DEBUG: user_id from token: {user_id}, type: {type(user_id)}")  # Отладочный вывод

        if user_id is None:
            raise credentials_exception

        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError) as e:
            print(f"DEBUG: Error converting user_id to int: {e}")  # Отладочный вывод
            raise credentials_exception

        user = db.query(User).filter(User.id == user_id_int).first()
        print(f"DEBUG: Found user: {user}")  # Отладочный вывод

        if user is None:
            raise credentials_exception
        return user
    except JWTError as e:
        print(f"DEBUG: JWTError: {e}")  # Отладочный вывод
        raise credentials_exception
