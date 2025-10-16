from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import models, schemas, auth
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth API", version="1.0.0")

# Хранилище для невалидных токенов (в продакшене использовать Redis)
blacklisted_tokens = set()


@app.post("/register", response_model=schemas.UserResponse)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # Проверка существования пользователя
    if auth.get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Создание пользователя
    hashed_password = auth.get_password_hash(user_data.password)
    db_user = models.User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@app.post("/login", response_model=schemas.Token)
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.UserResponse)
def get_current_user(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


@app.post("/logout")
def logout(
        credentials: auth.HTTPAuthorizationCredentials = Depends(auth.security),
        current_user: models.User = Depends(auth.get_current_user)
):
    # Добавляем токен в черный список
    blacklisted_tokens.add(credentials.credentials)
    return {"message": "Successfully logged out"}


# Middleware для проверки черного списка токенов
@app.middleware("http")
async def check_blacklisted_tokens(request, call_next):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        if token in blacklisted_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been invalidated"
            )

    response = await call_next(request)
    return response
