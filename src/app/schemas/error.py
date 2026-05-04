from sqlmodel import SQLModel

from src.utils.error import (
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    UnauthorizedError,
)


class ErrorSchema(SQLModel):
    message: str
    detail: str | None = None


class NotFoundErrorSchema(ErrorSchema):
    message: str = NotFoundError.message


class InternalServerErrorSchema(ErrorSchema):
    message: str = InternalServerError.message


class ForbiddenErrorSchema(ErrorSchema):
    message: str = ForbiddenError.message


class UnauthorizedErrorSchema(ErrorSchema):
    message: str = UnauthorizedError.message
