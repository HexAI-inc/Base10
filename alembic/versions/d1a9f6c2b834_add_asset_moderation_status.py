"""add_asset_moderation_status

Revision ID: d1a9f6c2b834
Revises: c8d3e5a1f047
Create Date: 2026-09-04 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1a9f6c2b834'
down_revision: Union[str, None] = 'c8d3e5a1f047'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    with op.batch_alter_table('assets', schema=None) as batch_op:
        existing_cols = [c['name'] for c in inspector.get_columns('assets')]
        if 'status' not in existing_cols:
            batch_op.add_column(sa.Column('status', sa.String(length=20), nullable=False, server_default='approved'))
        if 'review_notes' not in existing_cols:
            batch_op.add_column(sa.Column('review_notes', sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('assets', schema=None) as batch_op:
        batch_op.drop_column('review_notes')
        batch_op.drop_column('status')
