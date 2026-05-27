from sqlmodel import SQLModel

from src.utils.error import (
    BadRequestError,
    ConflictError,
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


class BadRequestErrorSchema(ErrorSchema):
    message: str = BadRequestError.message


class ConflictErrorSchema(ErrorSchema):
    message: str = ConflictError.message
