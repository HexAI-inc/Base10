"""add student profile and teacher message tables

Revision ID: 20251217_studentprofile
Revises: 2bf57f65397a
Create Date: 2025-12-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251217_studentprofile'
down_revision = '2bf57f65397a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create student_profiles table
    op.create_table(
        'student_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('classroom_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('strengths', sa.Text(), nullable=True),
        sa.Column('weaknesses', sa.Text(), nullable=True),
        sa.Column('learning_style', sa.String(length=100), nullable=True),
        sa.Column('participation_level', sa.String(length=20), nullable=True),
        sa.Column('homework_completion_rate', sa.Float(), nullable=True),
        sa.Column('last_contacted', sa.DateTime(), nullable=True),
        sa.Column('contact_frequency', sa.String(length=50), nullable=True),
        sa.Column('ai_context', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['teacher_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('classroom_id', 'student_id', name='uq_classroom_student')
    )
    op.create_index(op.f('ix_student_profiles_classroom_id'), 'student_profiles', ['classroom_id'], unique=False)
    op.create_index(op.f('ix_student_profiles_id'), 'student_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_student_profiles_student_id'), 'student_profiles', ['student_id'], unique=False)
    op.create_index(op.f('ix_student_profiles_teacher_id'), 'student_profiles', ['teacher_id'], unique=False)

    # Create teacher_messages table
    op.create_table(
        'teacher_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('classroom_id', sa.Integer(), nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('subject', sa.String(length=200), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('message_type', sa.String(length=50), nullable=True),
        sa.Column('is_read', sa.Boolean(), default=False, nullable=False),
        sa.Column('sent_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['teacher_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_teacher_messages_classroom_id'), 'teacher_messages', ['classroom_id'], unique=False)
    op.create_index(op.f('ix_teacher_messages_id'), 'teacher_messages', ['id'], unique=False)
    op.create_index(op.f('ix_teacher_messages_student_id'), 'teacher_messages', ['student_id'], unique=False)
    op.create_index(op.f('ix_teacher_messages_teacher_id'), 'teacher_messages', ['teacher_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_teacher_messages_teacher_id'), table_name='teacher_messages')
    op.drop_index(op.f('ix_teacher_messages_student_id'), table_name='teacher_messages')
    op.drop_index(op.f('ix_teacher_messages_id'), table_name='teacher_messages')
    op.drop_index(op.f('ix_teacher_messages_classroom_id'), table_name='teacher_messages')
    op.drop_table('teacher_messages')
    
    op.drop_index(op.f('ix_student_profiles_teacher_id'), table_name='student_profiles')
    op.drop_index(op.f('ix_student_profiles_student_id'), table_name='student_profiles')
    op.drop_index(op.f('ix_student_profiles_id'), table_name='student_profiles')
    op.drop_index(op.f('ix_student_profiles_classroom_id'), table_name='student_profiles')
    op.drop_table('student_profiles')
