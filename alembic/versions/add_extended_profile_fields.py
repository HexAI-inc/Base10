"""add_extended_profile_fields

Revision ID: add_extended_profile
Revises: 
Create Date: 2025-12-15

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_extended_profile'
down_revision = '74f36b352e31'  # Point to the latest migration
branch_labels = None
depends_on = None


def upgrade():
    # Add extended profile fields
    op.add_column('users', sa.Column('avatar_url', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('bio', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('country', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('location', sa.String(200), nullable=True))
    
    # Learning preferences
    op.add_column('users', sa.Column('learning_style', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('study_time_preference', sa.String(50), nullable=True))
    
    # Settings (JSON stored as strings)
    op.add_column('users', sa.Column('notification_settings', sa.String(1000), nullable=True))
    op.add_column('users', sa.Column('privacy_settings', sa.String(1000), nullable=True))
    
    # Gamification
    op.add_column('users', sa.Column('achievement_badges', sa.String(2000), nullable=True))
    op.add_column('users', sa.Column('total_points', sa.Integer(), nullable=True, default=0))
    op.add_column('users', sa.Column('level', sa.Integer(), nullable=True, default=1))


def downgrade():
    # Remove extended profile fields
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'bio')
    op.drop_column('users', 'country')
    op.drop_column('users', 'location')
    op.drop_column('users', 'learning_style')
    op.drop_column('users', 'study_time_preference')
    op.drop_column('users', 'notification_settings')
    op.drop_column('users', 'privacy_settings')
    op.drop_column('users', 'achievement_badges')
    op.drop_column('users', 'total_points')
    op.drop_column('users', 'level')
