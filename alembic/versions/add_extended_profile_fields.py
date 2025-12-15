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
    # Get connection to check for existing columns
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_columns = [col['name'] for col in inspector.get_columns('users')]
    
    # Only add columns if they don't exist
    columns_to_add = [
        ('avatar_url', sa.String(500)),
        ('bio', sa.String(500)),
        ('country', sa.String(100)),
        ('location', sa.String(200)),
        ('learning_style', sa.String(50)),
        ('study_time_preference', sa.String(50)),
        ('notification_settings', sa.String(1000)),
        ('privacy_settings', sa.String(1000)),
        ('achievement_badges', sa.String(2000)),
        ('total_points', sa.Integer()),
        ('level', sa.Integer()),
    ]
    
    for col_name, col_type in columns_to_add:
        if col_name not in existing_columns:
            if col_name == 'total_points':
                op.add_column('users', sa.Column(col_name, col_type, nullable=True, default=0))
            elif col_name == 'level':
                op.add_column('users', sa.Column(col_name, col_type, nullable=True, default=1))
            else:
                op.add_column('users', sa.Column(col_name, col_type, nullable=True))


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
