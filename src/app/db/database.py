from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.app import models  # noqa: F401
from src.app.core import settings

<<<<<<< HEAD
engine = create_async_engine(settings.form_db_url(), echo=settings.debug)
=======
engine = create_async_engine(settings.database_url, echo=settings.debug)
>>>>>>> 8712bd2 (Feature/database&migrations (#11))
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


<<<<<<< HEAD
<<<<<<< HEAD
async def get_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
=======
def create_db_and_tables():
    SQLModel.message_metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
>>>>>>> b48911e (Feature/database setup (#9))
=======
async def get_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
>>>>>>> 8712bd2 (Feature/database&migrations (#11))
        yield session
