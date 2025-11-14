"""add reminder preference fields

Revision ID: c0f0f1b2a4b4
Revises: 7d9dcecb266d
Create Date: 2025-08-21 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0f0f1b2a4b4'
down_revision: Union[str, None] = '7d9dcecb266d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('remind_morning', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('users', sa.Column('remind_day', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('users', sa.Column('remind_evening', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('users', sa.Column('last_morning_reminder', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('last_day_reminder', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('last_evening_reminder', sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'last_evening_reminder')
    op.drop_column('users', 'last_day_reminder')
    op.drop_column('users', 'last_morning_reminder')
    op.drop_column('users', 'remind_evening')
    op.drop_column('users', 'remind_day')
    op.drop_column('users', 'remind_morning')
