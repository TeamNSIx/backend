from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select

ModelT = TypeVar('ModelT', bound=SQLModel)


class BaseRepository(Generic[ModelT]):
    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    async def get_by_id(self, entity_id: UUID) -> ModelT | None:
        statement = select(self.model).where(self.model.id == entity_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_all(self) -> list[ModelT]:
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())

    async def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity
