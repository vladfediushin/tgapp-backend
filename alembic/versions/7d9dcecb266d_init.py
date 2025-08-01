"""init

Revision ID: 7d9dcecb266d
Revises: 
Create Date: 2025-07-31 21:24:32.981877

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7d9dcecb266d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_progress', sa.Column('repetition_count', sa.Integer(), nullable=True))
    op.execute('UPDATE user_progress SET repetition_count = 0 WHERE repetition_count IS NULL')
    op.alter_column('user_progress', 'repetition_count', nullable=False)
    op.add_column('user_progress', sa.Column('next_due_at', sa.DateTime(timezone=True), nullable=True))
    op.drop_column('user_progress', 'state')
    op.drop_column('user_progress', 'retrievability')
    op.drop_column('user_progress', 'reps')
    op.drop_column('user_progress', 'stability')
    op.drop_column('user_progress', 'last_review')
    op.drop_column('user_progress', 'due')
    op.drop_column('user_progress', 'difficulty')
    op.drop_column('user_progress', 'scheduled_days')
    op.drop_column('user_progress', 'elapsed_days')
    op.drop_column('user_progress', 'lapses')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_progress', sa.Column('lapses', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('user_progress', sa.Column('elapsed_days', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('user_progress', sa.Column('scheduled_days', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('user_progress', sa.Column('difficulty', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('user_progress', sa.Column('due', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
    op.add_column('user_progress', sa.Column('last_review', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
    op.add_column('user_progress', sa.Column('stability', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('user_progress', sa.Column('reps', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('user_progress', sa.Column('retrievability', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('user_progress', sa.Column('state', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('user_progress', 'next_due_at')
    op.drop_column('user_progress', 'repetition_count')
    # ### end Alembic commands ###
