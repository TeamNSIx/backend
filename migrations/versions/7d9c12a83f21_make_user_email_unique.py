"""make user email unique

Revision ID: 7d9c12a83f21
Revises: 72bc91efa403
Create Date: 2026-05-16 11:25:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '7d9c12a83f21'
down_revision: Union[str, Sequence[str], None] = '72bc91efa403'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
