"""add_new_subject_enums

Revision ID: a66d39049213
Revises: add_extended_profile
Create Date: 2025-12-15 17:14:41.735729

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a66d39049213'
down_revision: Union[str, None] = 'add_extended_profile'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new values to the subject enum
    # This only applies to PostgreSQL; SQLite doesn't use real enums
    connection = op.get_bind()
    if connection.dialect.name == 'postgresql':
        op.execute("ALTER TYPE subject ADD VALUE IF NOT EXISTS 'Government'")
        op.execute("ALTER TYPE subject ADD VALUE IF NOT EXISTS 'Civic Education'")
        op.execute("ALTER TYPE subject ADD VALUE IF NOT EXISTS 'Financial Accounting'")


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values directly
    # This would require creating a new enum type and migrating data
    pass
