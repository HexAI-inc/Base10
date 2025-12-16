"""add classroom lms tables

Revision ID: 20251216_add_classroom_lms
Revises: a66d39049213
Create Date: 2025-12-16 17:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251216_add_classroom_lms'
down_revision = 'a66d39049213'
branch_labels = None
depends_on = None


def upgrade():
    # Add columns to classrooms (only if the table already exists)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'classrooms' in inspector.get_table_names():
        with op.batch_alter_table('classrooms') as batch_op:
            batch_op.add_column(sa.Column('subject', sa.String(length=50), nullable=True))
            batch_op.add_column(sa.Column('grade_level', sa.String(length=20), nullable=True))

    # Add columns to assignments (only if the table already exists)
    if 'assignments' in inspector.get_table_names():
        with op.batch_alter_table('assignments') as batch_op:
            batch_op.add_column(sa.Column('assignment_type', sa.String(length=20), nullable=False, server_default='quiz'))
            batch_op.add_column(sa.Column('max_points', sa.Integer(), nullable=False, server_default='100'))
            batch_op.add_column(sa.Column('is_ai_generated', sa.Integer(), nullable=False, server_default='0'))
            batch_op.add_column(sa.Column('status', sa.String(length=20), nullable=False, server_default='draft'))

    # Create classroom_posts
    op.create_table(
        'classroom_posts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('classroom_id', sa.Integer(), sa.ForeignKey('classrooms.id'), nullable=False),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('post_type', sa.String(length=30), nullable=True),
        sa.Column('parent_post_id', sa.Integer(), sa.ForeignKey('classroom_posts.id'), nullable=True),
        sa.Column('attachment_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # Create classroom_materials
    op.create_table(
        'classroom_materials',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('classroom_id', sa.Integer(), sa.ForeignKey('classrooms.id'), nullable=False),
        sa.Column('uploaded_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('asset_id', sa.String(), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # Create submissions
    op.create_table(
        'submissions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('assignment_id', sa.Integer(), sa.ForeignKey('assignments.id'), nullable=False),
        sa.Column('student_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('content_text', sa.Text(), nullable=True),
        sa.Column('attachment_url', sa.String(), nullable=True),
        sa.Column('ai_suggested_score', sa.Integer(), nullable=True),
        sa.Column('ai_feedback_draft', sa.Text(), nullable=True),
        sa.Column('grade', sa.Integer(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('graded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_graded', sa.Integer(), nullable=False, server_default='0'),
    )


def downgrade():
    op.drop_table('submissions')
    op.drop_table('classroom_materials')
    op.drop_table('classroom_posts')
    with op.batch_alter_table('assignments') as batch_op:
        batch_op.drop_column('status')
        batch_op.drop_column('is_ai_generated')
        batch_op.drop_column('max_points')
        batch_op.drop_column('assignment_type')
    with op.batch_alter_table('classrooms') as batch_op:
        batch_op.drop_column('grade_level')
        batch_op.drop_column('subject')