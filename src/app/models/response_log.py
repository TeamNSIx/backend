from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class ResponseLog(SQLModel, table=True):
    __tablename__ = 'response_logs'

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    message_id: UUID = Field(foreign_key='messages.id')

    query_log_id: UUID = Field(foreign_key='query_logs.id')

    response_text: str

    used_fragments: Optional[dict] = Field(sa_column=Column(JSONB))

    response_time_ms: Optional[int] = None

    user_helpful: Optional[bool] = None

    created_at: datetime | None
