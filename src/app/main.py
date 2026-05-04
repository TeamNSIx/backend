from fastapi import FastAPI

from src.app.core import settings
from src.app.db.database import AsyncSessionLocal
from src.app.internal.bootstrap import run_bootstrap
from src.app.routers import api_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with AsyncSessionLocal() as session:
        await run_bootstrap(session)
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
app.include_router(api_router)
