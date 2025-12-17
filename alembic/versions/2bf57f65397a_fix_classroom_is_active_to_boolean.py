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
        # Check current column type
        result = bind.execute(sa.text("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'classrooms' AND column_name = 'is_active'
        """))
        current_type = result.fetchone()[0] if result.rowcount > 0 else None
        
        if current_type == 'integer':
            # Column is INTEGER, convert to BOOLEAN
            # First convert existing values: 1 -> true, 0 -> false, NULL -> false
            op.execute("UPDATE classrooms SET is_active = CASE WHEN is_active = 1 THEN 1 ELSE 0 END WHERE is_active IS NOT NULL")
            # Then alter the column type
            op.execute("ALTER TABLE classrooms ALTER COLUMN is_active TYPE BOOLEAN USING (CASE WHEN is_active = 1 THEN TRUE ELSE FALSE END)")
        elif current_type == 'boolean':
            # Already BOOLEAN, nothing to do
            pass
        else:
            # Unknown type, try to convert anyway
            op.execute("ALTER TABLE classrooms ALTER COLUMN is_active TYPE BOOLEAN USING (CASE WHEN is_active::integer = 1 THEN TRUE ELSE FALSE END)")
    
    elif dialect == 'sqlite':
        # SQLite: Already works with integers for booleans
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
