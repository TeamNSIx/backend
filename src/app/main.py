from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from src.app.db.database import create_db_and_tables


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


class Item(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None
