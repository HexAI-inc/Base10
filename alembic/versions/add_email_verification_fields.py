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
    # Add columns directly - Alembic handles "already exists" errors gracefully
    # SQLite and PostgreSQL handle this differently
    
    try:
        op.add_column('users', sa.Column('verification_token', sa.String(length=255), nullable=True))
        print("✅ Added verification_token column")
    except Exception as e:
        print(f"⏭️ verification_token: {e}")
    
    try:
        op.add_column('users', sa.Column('verification_token_expires', sa.DateTime(timezone=True), nullable=True))
        print("✅ Added verification_token_expires column")
    except Exception as e:
        print(f"⏭️ verification_token_expires: {e}")
    
    try:
        op.add_column('users', sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True))
        print("✅ Added verified_at column")
    except Exception as e:
        print(f"⏭️ verified_at: {e}")
    
    try:
        op.add_column('users', sa.Column('role', sa.String(length=50), nullable=True, server_default='student'))
        print("✅ Added role column")
    except Exception as e:
        print(f"⏭️ role: {e}")
    
    try:
        op.add_column('users', sa.Column('username', sa.String(length=100), nullable=True, unique=True))
        print("✅ Added username column")
    except Exception as e:
        print(f"⏭️ username: {e}")


def downgrade():
    # Drop columns if they exist
    try:
        op.drop_column('users', 'username')
    except Exception:
        pass
    
    try:
        op.drop_column('users', 'role')
    except Exception:
        pass
    
    try:
        op.drop_column('users', 'verified_at')
    except Exception:
        pass
    
    try:
        op.drop_column('users', 'verification_token_expires')
    except Exception:
        pass
    
    try:
        op.drop_column('users', 'verification_token')
    except Exception:
        pass
