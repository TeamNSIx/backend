from typing import Annotated

from fastapi import Depends

from src.app.schemas.pagination import PaginationParams

PaginationDep = Annotated[PaginationParams, Depends()]
