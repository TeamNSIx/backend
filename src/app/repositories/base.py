from datetime import datetime
from enum import Enum
from typing import Generic, TypeAlias, TypeVar
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.app.models.base_model import BaseModel

ModelT = TypeVar('ModelT', bound=BaseModel)
ScalarFilterValue: TypeAlias = str | int | bool | float | UUID | datetime | Enum | None
UpdateValue: TypeAlias = ScalarFilterValue | dict | list


class BaseRepository(Generic[ModelT]):
    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    def _apply_filters(self, statement, **filters: ScalarFilterValue):
        for field_name, value in filters.items():
            if not hasattr(self.model, field_name):
                msg = (
                    f"Unknown filter field '{field_name}' "
                    f"for model {self.model.__name__}"
                )
                raise ValueError(msg)
            statement = statement.where(getattr(self.model, field_name) == value)
        return statement

    async def get_by_id(self, entity_id: UUID) -> ModelT | None:
        statement = select(self.model).where(self.model.id == entity_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def count(self, **filters: ScalarFilterValue) -> int:
        statement = select(func.count()).select_from(self.model)
        statement = self._apply_filters(statement, **filters)
        result = await self.session.execute(statement)
        return int(result.scalar_one())

    async def get_page(
        self,
        offset: int,
        limit: int,
        *,
        order_asc: bool = False,
        **filters: ScalarFilterValue,
    ) -> list[ModelT]:
        statement = select(self.model)
        statement = self._apply_filters(statement, **filters)
        if hasattr(self.model, 'created_at'):
            created_at = self.model.created_at
            statement = statement.order_by(
                created_at.asc() if order_asc else created_at.desc(),
            )
        statement = statement.offset(offset).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_all(self, **filters: ScalarFilterValue) -> list[ModelT]:
        statement = select(self.model)
        statement = self._apply_filters(statement, **filters)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def save(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update_fields(
        self,
        entity_id: UUID,
        updates: dict[str, UpdateValue],
    ) -> ModelT | None:
        entity = await self.get_by_id(entity_id)
        if entity is None:
            return None

        for field_name, value in updates.items():
            if not hasattr(self.model, field_name):
                msg = (
                    f"Unknown update field '{field_name}' "
                    f"for model {self.model.__name__}"
                )
                raise ValueError(msg)
            setattr(entity, field_name, value)

        await self.session.commit()
        await self.session.refresh(entity)
        return entity
