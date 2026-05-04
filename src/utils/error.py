class NotFoundError(Exception):
    message = 'Not found'

class InternalServerError(Exception):
    message = 'Internal Server Error'

class ForbiddenError(Exception):
    message = 'Access denied'

class UnauthorizedError(Exception):
    message = 'You are not authorized'