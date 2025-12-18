"""add ai quota and onboarding fields to user

Revision ID: 20251218_ai_quota_onboarding
Revises: 20251217_set_admin_roles
Create Date: 2025-12-18 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251218_ai_quota_onboarding'
down_revision = '20251217_set_admin_roles'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add AI Quota fields
    op.add_column('users', sa.Column('ai_quota_limit', sa.Integer(), nullable=True, server_default='100'))
    op.add_column('users', sa.Column('ai_quota_used', sa.Integer(), nullable=True, server_default='0'))
    
    # Add Onboarding fields
    op.add_column('users', sa.Column('is_onboarded', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('users', sa.Column('onboarding_step', sa.Integer(), nullable=True, server_default='0'))
    
    # Update existing rows to have the defaults
    op.execute("UPDATE users SET ai_quota_limit = 100 WHERE ai_quota_limit IS NULL")
    op.execute("UPDATE users SET ai_quota_used = 0 WHERE ai_quota_used IS NULL")
    op.execute("UPDATE users SET is_onboarded = false WHERE is_onboarded IS NULL")
    op.execute("UPDATE users SET onboarding_step = 0 WHERE onboarding_step IS NULL")


def downgrade() -> None:
    op.drop_column('users', 'onboarding_step')
    op.drop_column('users', 'is_onboarded')
    op.drop_column('users', 'ai_quota_used')
    op.drop_column('users', 'ai_quota_limit')
