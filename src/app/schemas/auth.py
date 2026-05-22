from pydantic import BaseModel, EmailStr, Field, SecretStr

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
    email: EmailStr
    password: SecretStr


class RegisterResponse(BaseModel):
    success: bool
    user: UserPublic
    message: str | None = None


class ConfirmAccountData(BaseModel):
    token: str = Field(min_length=1)


class ChangePasswordData(BaseModel):
    current_password: SecretStr
    new_password: SecretStr = Field(min_length=8)


class SuccessResponse(BaseModel):
    success: bool = True
    message: str | None = None
