"""add bot messaging status fields

Revision ID: 4c3f9770d2c1
Revises: c0f0f1b2a4b4
Create Date: 2025-08-21 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c3f9770d2c1'
down_revision: Union[str, None] = 'c0f0f1b2a4b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_bot_blocked', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('users', sa.Column('last_bot_message_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('last_bot_interaction_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'last_bot_interaction_at')
    op.drop_column('users', 'last_bot_message_at')
    op.drop_column('users', 'is_bot_blocked')
