from fastapi import FastAPI

from src.app.core import settings
from src.app.routers import api_router

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(api_router)
