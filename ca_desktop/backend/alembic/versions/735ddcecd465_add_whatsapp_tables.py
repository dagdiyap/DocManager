"""add_whatsapp_tables

Revision ID: 735ddcecd465
Revises: bf8a455fc811
Create Date: 2026-03-02 10:00:20.910905

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '735ddcecd465'
down_revision: Union[str, None] = 'bf8a455fc811'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create document_uploads table
    op.create_table(
        'document_uploads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_phone', sa.String(length=15), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.Text(), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('processed', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['client_phone'], ['clients.phone_number'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_uploads_client', 'document_uploads', ['client_phone'])
    op.create_index('idx_uploads_processed', 'document_uploads', ['processed'])
    
    # Create whatsapp_bot_state table
    op.create_table(
        'whatsapp_bot_state',
        sa.Column('phone_number', sa.String(length=15), nullable=False),
        sa.Column('bot_enabled', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('last_interaction', sa.DateTime(), nullable=True),
        sa.Column('current_flow', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('phone_number')
    )


def downgrade() -> None:
    op.drop_index('idx_uploads_processed', table_name='document_uploads')
    op.drop_index('idx_uploads_client', table_name='document_uploads')
    op.drop_table('document_uploads')
    op.drop_table('whatsapp_bot_state')
