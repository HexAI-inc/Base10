"""set admin role for legacy accounts

Revision ID: 20251217_set_admin_roles
Revises: 20251217_studentprofile
Create Date: 2025-12-17

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251217_set_admin_roles'
down_revision = '20251217_studentprofile'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Set admin role for legacy admin accounts
    op.execute("""
        UPDATE users 
        SET role = 'admin' 
        WHERE email IN ('esjallow03@gmail.com')
        AND role != 'admin'
    """)
    
    # Log the change
    op.execute("""
        UPDATE users 
        SET updated_at = CURRENT_TIMESTAMP 
        WHERE email IN ('esjallow03@gmail.com')
    """)


def downgrade() -> None:
    # Revert admin accounts to student role (if needed for rollback)
    op.execute("""
        UPDATE users 
        SET role = 'student' 
        WHERE email IN ('esjallow03@gmail.com')
        AND role = 'admin'
    """)
