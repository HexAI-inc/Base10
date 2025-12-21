"""fix_userrole_enum_data_mismatch

Revision ID: 69bfa27d9f46
Revises: f9c39d9b31f2
Create Date: 2025-12-21 00:54:49.755590

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '69bfa27d9f46'
down_revision: Union[str, None] = 'f9c39d9b31f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Handle userrole enum data mismatch - ensure enum uses lowercase values
    # This migration is specifically for PostgreSQL production database
    
    # Check if we're running on PostgreSQL
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        # Convert to VARCHAR temporarily to allow data manipulation
        op.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(20) USING role::text")
        
        # Drop the existing enum if it exists
        op.execute("DROP TYPE IF EXISTS userrole CASCADE")
        
        # Create the enum with correct lowercase values
        op.execute("CREATE TYPE userrole AS ENUM ('student', 'teacher', 'admin', 'moderator')")
        
        # Normalize role data to match enum values
        op.execute("""
            UPDATE users SET role = CASE 
                WHEN LOWER(COALESCE(role, '')) = 'student' THEN 'student'
                WHEN LOWER(COALESCE(role, '')) = 'teacher' THEN 'teacher' 
                WHEN LOWER(COALESCE(role, '')) = 'admin' THEN 'admin'
                WHEN LOWER(COALESCE(role, '')) = 'administrator' THEN 'admin'
                WHEN LOWER(COALESCE(role, '')) = 'moderator' THEN 'moderator'
                WHEN COALESCE(role, '') = 'STUDENT' THEN 'student'
                WHEN COALESCE(role, '') = 'TEACHER' THEN 'teacher'
                WHEN COALESCE(role, '') = 'ADMIN' THEN 'admin'
                WHEN COALESCE(role, '') = 'MODERATOR' THEN 'moderator'
                ELSE 'student'  -- Default to student for any invalid values
            END WHERE role IS NOT NULL OR role = ''
        """)
        
        # Convert back to enum
        op.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::userrole")
    else:
        # For other databases (like SQLite for testing), just ensure data is normalized
        # This is a no-op for non-PostgreSQL databases
        pass


def downgrade() -> None:
    # Convert back to VARCHAR for downgrade (PostgreSQL only)
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(20) USING role::text")
        op.execute("DROP TYPE IF EXISTS userrole CASCADE")
