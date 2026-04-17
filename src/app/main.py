from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.app.db.database import create_db_and_tables

app = FastAPI(lifespan=lifespan)

@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
