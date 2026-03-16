from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class QueryLog(SQLModel, table=True):
    __tablename__ = 'query_logs'

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    user_id: UUID = Field(foreign_key='users.id')

    query_text: str

    search_results: Optional[dict] = Field(sa_column=Column(JSONB))

    created_at: datetime | None
