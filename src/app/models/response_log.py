from typing import Optional
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from app.models.base_model import BaseModel


class ResponseLog(BaseModel, table=True):
    __tablename__ = 'response_logs'

    message_id: UUID = Field(foreign_key='messages.id')
    query_log_id: UUID = Field(foreign_key='query_logs.id')
    response_text: str
    used_fragments: Optional[dict] = Field(sa_column=Column(JSONB))
    response_time_ms: Optional[int] = None
    user_helpful: Optional[bool] = None
