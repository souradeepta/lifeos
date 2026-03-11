"""add recurring plans

Revision ID: a1b2c3d4e5f6
Revises: 63dacdfb4103
Create Date: 2026-03-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '63dacdfb4103'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'recurring_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('goal_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column(
            'recurrence_type',
            sa.Enum('DAILY', 'WEEKDAYS', 'WEEKLY', name='recurrencetype'),
            nullable=False,
        ),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'recurring_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recurring_plan_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['recurring_plan_id'], ['recurring_plans.id'], ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.add_column(
        'plans',
        sa.Column('recurring_plan_id', sa.Integer(), nullable=True),
    )
    # SQLite does not support ADD CONSTRAINT via ALTER TABLE, so we skip FK
    # enforcement here — the ORM relationship handles integrity at the app level.


def downgrade() -> None:
    with op.batch_alter_table('plans') as batch_op:
        batch_op.drop_column('recurring_plan_id')
    op.drop_table('recurring_tasks')
    op.drop_table('recurring_plans')
