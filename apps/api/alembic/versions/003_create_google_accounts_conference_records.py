from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'google_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('google_user_id', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=False),
        sa.Column('token_expiry', sa.DateTime(timezone=True), nullable=True),
        sa.Column('scopes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_google_accounts_company_id'), 'google_accounts', ['company_id'])
    op.create_index(op.f('ix_google_accounts_google_user_id'), 'google_accounts', ['google_user_id'])

    op.create_table(
        'conference_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('google_account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider_conference_id', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('meeting_link', sa.String(length=500), nullable=True),
        sa.Column('conference_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('conference_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('transcript', sa.Text(), nullable=True),
        sa.Column('smart_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id']),
        sa.ForeignKeyConstraint(['google_account_id'], ['google_accounts.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_conference_records_meeting_id'), 'conference_records', ['meeting_id'])
    op.create_index(op.f('ix_conference_records_google_account_id'), 'conference_records', ['google_account_id'])


def downgrade():
    op.drop_index(op.f('ix_conference_records_google_account_id'), table_name='conference_records')
    op.drop_index(op.f('ix_conference_records_meeting_id'), table_name='conference_records')
    op.drop_table('conference_records')
    op.drop_index(op.f('ix_google_accounts_google_user_id'), table_name='google_accounts')
    op.drop_index(op.f('ix_google_accounts_company_id'), table_name='google_accounts')
    op.drop_table('google_accounts')
