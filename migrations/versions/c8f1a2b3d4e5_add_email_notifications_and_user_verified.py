"""add email notifications and user verified flag

Revision ID: c8f1a2b3d4e5
Revises: 7d9c12a83f21
Create Date: 2026-05-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'c8f1a2b3d4e5'
down_revision: Union[str, Sequence[str], None] = '7d9c12a83f21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
    )
    op.create_table(
        'email_notifications',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=True),
        sa.Column('notification_type', sa.String(), nullable=False),
        sa.Column('recipient', sa.String(), nullable=False),
        sa.Column('subject', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_email_notifications_recipient'),
        'email_notifications',
        ['recipient'],
        unique=False,
    )
    op.create_index(
        op.f('ix_email_notifications_status'),
        'email_notifications',
        ['status'],
        unique=False,
    )
    op.create_index(
        op.f('ix_email_notifications_user_id'),
        'email_notifications',
        ['user_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_email_notifications_user_id'), table_name='email_notifications')
    op.drop_index(op.f('ix_email_notifications_status'), table_name='email_notifications')
    op.drop_index(
        op.f('ix_email_notifications_recipient'),
        table_name='email_notifications',
    )
    op.drop_table('email_notifications')
    op.drop_column('users', 'is_verified')
