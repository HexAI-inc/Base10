"""Add psychometric fields to attempts

Revision ID: 7db8b1ebb741
Revises: 
Create Date: 2024-01-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7db8b1ebb741'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add psychometric tracking fields to attempts table
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    # Create users table if it doesn't exist
    if 'users' not in tables:
        op.create_table('users',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('email', sa.String(length=255), nullable=False, unique=True),
            sa.Column('hashed_password', sa.String(length=255), nullable=False),
            sa.Column('full_name', sa.String(length=255), nullable=True),
            sa.Column('is_active', sa.Boolean(), default=True),
            sa.Column('is_superuser', sa.Boolean(), default=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
        )
        tables.append('users')

    # Create questions table if it doesn't exist
    if 'questions' not in tables:
        op.create_table('questions',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('text', sa.Text(), nullable=False),
            sa.Column('subject', sa.String(length=100), nullable=False),
            sa.Column('topic', sa.String(length=100), nullable=True),
            sa.Column('difficulty', sa.String(length=20), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
        )
        tables.append('questions')

    # If the attempts table doesn't exist (fresh DB), create a minimal attempts table
    if 'attempts' not in tables:
        op.create_table('attempts',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('question_id', sa.Integer(), sa.ForeignKey('questions.id'), nullable=False),
            sa.Column('is_correct', sa.Boolean(), nullable=False, server_default=sa.text('false')),
            sa.Column('selected_option', sa.Integer(), nullable=True),
            sa.Column('attempted_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
        )

    # Ensure columns exist before adding
    existing_cols = inspector.get_columns('attempts') if 'attempts' in inspector.get_table_names() else []
    col_names = [c['name'] for c in existing_cols]
    if 'time_taken_ms' not in col_names:
        op.add_column('attempts', sa.Column('time_taken_ms', sa.Integer(), nullable=True))
    if 'confidence_level' not in col_names:
        op.add_column('attempts', sa.Column('confidence_level', sa.Integer(), nullable=True))
    if 'network_type' not in col_names:
        op.add_column('attempts', sa.Column('network_type', sa.String(length=20), nullable=True))
    if 'app_version' not in col_names:
        op.add_column('attempts', sa.Column('app_version', sa.String(length=20), nullable=True))
    
    # Create classroom tables
    op.create_table('classrooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('join_code', sa.String(length=12), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['teacher_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_classrooms_id'), 'classrooms', ['id'], unique=False)
    op.create_index(op.f('ix_classrooms_join_code'), 'classrooms', ['join_code'], unique=True)
    op.create_index(op.f('ix_classrooms_teacher_id'), 'classrooms', ['teacher_id'], unique=False)
    
    # Create assignments table
    op.create_table('assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('classroom_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('subject', sa.String(length=50), nullable=True),
        sa.Column('topic', sa.String(length=100), nullable=True),
        sa.Column('difficulty', sa.String(length=20), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assignments_classroom_id'), 'assignments', ['classroom_id'], unique=False)
    op.create_index(op.f('ix_assignments_id'), 'assignments', ['id'], unique=False)
    
    # Create classroom_students association table
    op.create_table('classroom_students',
        sa.Column('classroom_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('classroom_id', 'student_id')
    )


def downgrade() -> None:
    # Drop classroom tables
    op.drop_table('classroom_students')
    op.drop_index(op.f('ix_assignments_id'), table_name='assignments')
    op.drop_index(op.f('ix_assignments_classroom_id'), table_name='assignments')
    op.drop_table('assignments')
    op.drop_index(op.f('ix_classrooms_teacher_id'), table_name='classrooms')
    op.drop_index(op.f('ix_classrooms_join_code'), table_name='classrooms')
    op.drop_index(op.f('ix_classrooms_id'), table_name='classrooms')
    op.drop_table('classrooms')
    
    # Remove psychometric fields
    op.drop_column('attempts', 'app_version')
    op.drop_column('attempts', 'network_type')
    op.drop_column('attempts', 'confidence_level')
    op.drop_column('attempts', 'time_taken_ms')
