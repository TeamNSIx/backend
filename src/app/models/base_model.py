from datetime import datetime
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel, table=False):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={'server_default': func.now(), 'nullable': False},
    )


class BasePublic(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
