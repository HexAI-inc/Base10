"""add_admin_activity_log

Revision ID: c8d3e5a1f047
Revises: b4f2a1c9e3d7
Create Date: 2026-09-03 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8d3e5a1f047'
down_revision: Union[str, None] = 'b4f2a1c9e3d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'admin_activity_logs' not in tables:
        op.create_table(
            'admin_activity_logs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('admin_id', sa.Integer(), nullable=False),
            sa.Column('action_type', sa.String(length=50), nullable=False),
            sa.Column('action_description', sa.Text(), nullable=False),
            sa.Column('target_type', sa.String(length=50), nullable=True),
            sa.Column('target_id', sa.Integer(), nullable=True),
            sa.Column('metadata_json', sa.JSON(), nullable=True),
            sa.Column('ip_address', sa.String(length=45), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
            sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_admin_activity_logs_id'), 'admin_activity_logs', ['id'], unique=False)
        op.create_index(op.f('ix_admin_activity_logs_admin_id'), 'admin_activity_logs', ['admin_id'], unique=False)
        op.create_index(op.f('ix_admin_activity_logs_action_type'), 'admin_activity_logs', ['action_type'], unique=False)
        op.create_index(op.f('ix_admin_activity_logs_created_at'), 'admin_activity_logs', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_admin_activity_logs_created_at'), table_name='admin_activity_logs')
    op.drop_index(op.f('ix_admin_activity_logs_action_type'), table_name='admin_activity_logs')
    op.drop_index(op.f('ix_admin_activity_logs_admin_id'), table_name='admin_activity_logs')
    op.drop_index(op.f('ix_admin_activity_logs_id'), table_name='admin_activity_logs')
    op.drop_table('admin_activity_logs')
