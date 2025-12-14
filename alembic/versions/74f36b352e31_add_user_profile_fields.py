"""add_user_profile_fields

Revision ID: 74f36b352e31
Revises: 7db8b1ebb741
Create Date: 2025-12-14 18:41:17.233226

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74f36b352e31'
down_revision: Union[str, None] = '7db8b1ebb741'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add user profile fields for content filtering and engagement tracking
    op.add_column('users', sa.Column('education_level', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('target_exam_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('preferred_subjects', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('has_app_installed', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('users', sa.Column('study_streak', sa.Integer(), server_default='0', nullable=False))
    op.add_column('users', sa.Column('last_activity_date', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove user profile fields
    op.drop_column('users', 'last_activity_date')
    op.drop_column('users', 'study_streak')
    op.drop_column('users', 'has_app_installed')
    op.drop_column('users', 'preferred_subjects')
    op.drop_column('users', 'target_exam_date')
    op.drop_column('users', 'education_level')
