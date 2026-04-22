from fastapi import APIRouter

from src.app.routers.conversations import router as conversations_router
from src.app.routers.users import router as users_router

api_router = APIRouter(prefix='/api/v1')
api_router.include_router(users_router)
api_router.include_router(conversations_router)
