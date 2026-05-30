"""change embedding vector size to 384

Revision ID: f1c2d3e4a5b6
Revises: c8f1a2b3d4e5
Create Date: 2026-05-27 20:55:00.000000

"""

from typing import Sequence, Union

import pgvector.sqlalchemy
import sqlalchemy as sa
from alembic import op

revision: str = 'f1c2d3e4a5b6'
down_revision: Union[str, Sequence[str], None] = 'c8f1a2b3d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('DELETE FROM embeddings')
    op.drop_column('embeddings', 'embedding')
    op.add_column(
        'embeddings',
        sa.Column(
            'embedding',
            pgvector.sqlalchemy.Vector(dim=384),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.execute('DELETE FROM embeddings')
    op.drop_column('embeddings', 'embedding')
    op.add_column(
        'embeddings',
        sa.Column(
            'embedding',
            pgvector.sqlalchemy.Vector(dim=1536),
            nullable=True,
        ),
    )
