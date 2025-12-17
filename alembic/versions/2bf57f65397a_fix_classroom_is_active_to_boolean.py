"""fix_classroom_is_active_to_boolean

Revision ID: 2bf57f65397a
Revises: 20251216_merge_heads
Create Date: 2025-12-17 08:07:50.600116

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2bf57f65397a'
down_revision: Union[str, None] = '20251216_merge_heads'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if we're on PostgreSQL or SQLite
    bind = op.get_bind()
    dialect = bind.dialect.name
    
    if dialect == 'postgresql':
        # PostgreSQL: Convert integer to boolean
        # First convert existing values: 1 -> true, 0 -> false, NULL -> false
        op.execute("UPDATE classrooms SET is_active = CASE WHEN is_active = 1 THEN true ELSE false END")
        # Then alter the column type
        op.execute("ALTER TABLE classrooms ALTER COLUMN is_active TYPE BOOLEAN USING (is_active::integer::boolean)")
    elif dialect == 'sqlite':
        # SQLite: Already works with integers for booleans, but let's ensure consistency
        # SQLite doesn't have ALTER COLUMN TYPE, so we use Python default handling
        pass


def downgrade() -> None:
    # Check if we're on PostgreSQL or SQLite
    bind = op.get_bind()
    dialect = bind.dialect.name
    
    if dialect == 'postgresql':
        # Convert boolean back to integer for rollback
        op.execute("ALTER TABLE classrooms ALTER COLUMN is_active TYPE INTEGER USING (CASE WHEN is_active THEN 1 ELSE 0 END)")
    elif dialect == 'sqlite':
        pass
