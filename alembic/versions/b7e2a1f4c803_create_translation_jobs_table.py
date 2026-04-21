"""create translation_jobs table

Revision ID: b7e2a1f4c803
Revises: 01da4c6011d9
Create Date: 2026-04-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'b7e2a1f4c803'
down_revision: Union[str, Sequence[str], None] = '01da4c6011d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'translation_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', name='jobstatus'), nullable=False),
        sa.Column('language', sa.String(), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('sheet_prompts', JSONB(), nullable=False),
        sa.Column('file_key', sa.String(), nullable=False),
        sa.Column('bucket', sa.String(), nullable=False),
        sa.Column('result_file_key', sa.String(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_translation_jobs_id'), 'translation_jobs', ['id'], unique=False)
    op.create_index(op.f('ix_translation_jobs_user_id'), 'translation_jobs', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_translation_jobs_user_id'), table_name='translation_jobs')
    op.drop_index(op.f('ix_translation_jobs_id'), table_name='translation_jobs')
    op.drop_table('translation_jobs')
    op.execute("DROP TYPE jobstatus")
