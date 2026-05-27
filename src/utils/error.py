class AppError(Exception):
    message: str = 'Application error'
    status_code: int = 500

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail
        super().__init__(self.detail or self.message)


class NotFoundError(AppError):
    message = 'Not found'
    status_code = 404


class InternalServerError(AppError):
    message = 'Internal Server Error'
    status_code = 500


class ForbiddenError(AppError):
    message = 'Access denied'
    status_code = 403


class UnauthorizedError(AppError):
    message = 'You are not authorized'
    status_code = 401


class BadRequestError(AppError):
    message = 'Bad request'
    status_code = 400


class ConflictError(AppError):
    message = 'Conflict'
    status_code = 409
