from typing import Optional
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from app.models.base_model import BaseModel


class QueryLog(BaseModel, table=True):
    __tablename__ = 'query_logs'

    user_id: UUID = Field(foreign_key='users.id')
    query_text: str
    search_results: Optional[dict] = Field(sa_column=Column(JSONB))
