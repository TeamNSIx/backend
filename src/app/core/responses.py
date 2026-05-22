from src.app.schemas.error import (
    BadRequestErrorSchema,
    ConflictErrorSchema,
    ForbiddenErrorSchema,
    InternalServerErrorSchema,
    NotFoundErrorSchema,
    UnauthorizedErrorSchema,
)

common_responses = {
    500: {'model': InternalServerErrorSchema},
}

auth_responses = {
    401: {'model': UnauthorizedErrorSchema},
    403: {'model': ForbiddenErrorSchema},
}

detail_responses = {
    404: {'model': NotFoundErrorSchema},
}

bad_request_responses = {
    400: {'model': BadRequestErrorSchema},
}

conflict_responses = {
    409: {'model': ConflictErrorSchema},
}


def merge_responses(*parts: dict) -> dict:
    merged: dict = {}
    for part in parts:
        merged.update(part)
    return merged
