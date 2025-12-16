"""merge heads add_email_verification + classroom_lms

Revision ID: 20251216_merge_heads
Revises: add_email_verification, 20251216_add_classroom_lms
Create Date: 2025-12-16 21:50:00.000000
"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision = '20251216_merge_heads'
down_revision = ('add_email_verification', '20251216_add_classroom_lms')
branch_labels = None
depends_on = None


def upgrade():
    # This is a merge migration to resolve multiple heads.
    # No schema changes required; it consolidates the migration history.
    pass


def downgrade():
    # No-op: do not try to un-merge
    pass
