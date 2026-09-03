"""add_transaction_model_and_user_subscription_fields

Revision ID: b4f2a1c9e3d7
Revises: c06b30945ea0
Create Date: 2026-09-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4f2a1c9e3d7'
down_revision: Union[str, None] = 'c06b30945ea0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'transactions' not in tables:
        op.create_table(
            'transactions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('client_reference', sa.String(length=100), nullable=False),
            sa.Column('transaction_id', sa.String(length=100), nullable=True),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('plan_id', sa.String(length=50), nullable=False),
            sa.Column('amount', sa.String(length=20), nullable=False),
            sa.Column('currency', sa.String(length=10), nullable=False),
            sa.Column('provider', sa.String(length=20), nullable=False, server_default='WAVE'),
            sa.Column('status', sa.String(length=20), nullable=False, server_default='PENDING'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)
        op.create_index(op.f('ix_transactions_client_reference'), 'transactions', ['client_reference'], unique=True)
        op.create_index(op.f('ix_transactions_user_id'), 'transactions', ['user_id'], unique=False)

    with op.batch_alter_table('users', schema=None) as batch_op:
        existing_cols = [c['name'] for c in inspector.get_columns('users')]
        if 'subscription_plan' not in existing_cols:
            batch_op.add_column(sa.Column('subscription_plan', sa.String(length=50), nullable=True))
        if 'subscription_status' not in existing_cols:
            batch_op.add_column(sa.Column('subscription_status', sa.String(length=20), nullable=True))
        if 'subscription_expires_at' not in existing_cols:
            batch_op.add_column(sa.Column('subscription_expires_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('subscription_expires_at')
        batch_op.drop_column('subscription_status')
        batch_op.drop_column('subscription_plan')

    op.drop_index(op.f('ix_transactions_user_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_client_reference'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_id'), table_name='transactions')
    op.drop_table('transactions')
