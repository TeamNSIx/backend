from pydantic import BaseModel, SecretStr

from src.app.models.user import UserCreate, UserPublic


class AuthData(BaseModel):
    username: str
    password: SecretStr

class TokenData(BaseModel):
    token: str


class UserTokenData(BaseModel):
    user_id: str
    token_id: str


class AuthTokenData(BaseModel):
    access_token: str
    refresh_token: str


class RegisterData(UserCreate):
    password: SecretStr


class RegisterResponse(BaseModel):
    success: bool
    user: UserPublic