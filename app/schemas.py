from pydantic import BaseModel, EmailStr, validator
from datetime import datetime

from pydantic import BaseModel, EmailStr, validator
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

    @validator('password')
    def password_min_length(cls, v):
        if len(v) < 3:
            raise ValueError('Password must be at least 3 characters long')
        return v

    @validator('username')
    def username_min_length(cls, v):
        if len(v) < 2:
            raise ValueError('Username must be at least 2 characters long')
        return v


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int = None
