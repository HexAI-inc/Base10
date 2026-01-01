"""ensure_email_unique_optional_constraint

Revision ID: 09003ed9cc7d
Revises: 69bfa27d9f46
Create Date: 2025-12-21 12:24:17.628373

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '09003ed9cc7d'
down_revision: Union[str, None] = '69bfa27d9f46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure email column is unique and nullable
    # This migration ensures the database constraint matches the SQLAlchemy model
    
    # Check if we're running on PostgreSQL
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        # Drop existing unique index if it exists (to recreate it properly)
        op.execute("DROP INDEX IF EXISTS ix_users_email")
        
        # Create unique index that allows NULL values
        # In PostgreSQL, unique indexes allow multiple NULL values by default
        op.create_index('ix_users_email', 'users', ['email'], unique=True)
        
        # Ensure the column is nullable
        op.alter_column('users', 'email', nullable=True, existing_type=sa.String())
    
    # For other databases, the SQLAlchemy model should handle this


def downgrade() -> None:
    # Revert changes - but since we're just ensuring constraints exist,
    # we don't need to remove them in downgrade
    pass
