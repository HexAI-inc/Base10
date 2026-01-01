"""add email verification fields

Revision ID: add_email_verification
Revises: a66d39049213
Create Date: 2025-12-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_email_verification'
down_revision = 'a66d39049213'  # Points to add_new_subject_enums
branch_labels = None
depends_on = None


def upgrade():
    # Get connection and check if columns exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_columns = [col['name'] for col in inspector.get_columns('users')]
    
    # Add verification_token if it doesn't exist
    if 'verification_token' not in existing_columns:
        op.add_column('users', sa.Column('verification_token', sa.String(length=255), nullable=True))
        print("✅ Added verification_token column")
    else:
        print("⏭️ verification_token column already exists, skipping")
    
    # Add verification_token_expires if it doesn't exist
    if 'verification_token_expires' not in existing_columns:
        op.add_column('users', sa.Column('verification_token_expires', sa.DateTime(timezone=True), nullable=True))
        print("✅ Added verification_token_expires column")
    else:
        print("⏭️ verification_token_expires column already exists, skipping")
    
    # Add verified_at if it doesn't exist
    if 'verified_at' not in existing_columns:
        op.add_column('users', sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True))
        print("✅ Added verified_at column")
    else:
        print("⏭️ verified_at column already exists, skipping")
    
    # Add role if it doesn't exist (for onboarding flows)
    if 'role' not in existing_columns:
        op.add_column('users', sa.Column('role', sa.String(length=50), nullable=True, server_default='student'))
        print("✅ Added role column")
    else:
        print("⏭️ role column already exists, skipping")
    
    # Add username if it doesn't exist
    if 'username' not in existing_columns:
        op.add_column('users', sa.Column('username', sa.String(length=100), nullable=True, unique=True))
        print("✅ Added username column")
    else:
        print("⏭️ username column already exists, skipping")


def downgrade():
    # Get connection and check if columns exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'username' in existing_columns:
        op.drop_column('users', 'username')
    
    if 'role' in existing_columns:
        op.drop_column('users', 'role')
    
    if 'verified_at' in existing_columns:
        op.drop_column('users', 'verified_at')
    
    if 'verification_token_expires' in existing_columns:
        op.drop_column('users', 'verification_token_expires')
    
    if 'verification_token' in existing_columns:
        op.drop_column('users', 'verification_token')
