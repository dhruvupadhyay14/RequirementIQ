from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    project_status = sa.Enum(
        'Draft',
        'Discovery',
        'Requirement Gathering',
        'Proposal',
        'Development',
        'Completed',
        'Archived',
        name='projectstatus',
    )
    project_priority = sa.Enum(
        'Low',
        'Medium',
        'High',
        'Critical',
        name='projectpriority',
    )
    meeting_provider = sa.Enum(
        'GOOGLE_MEET',
        'ZOOM',
        'MICROSOFT_TEAMS',
        'MANUAL',
        name='meetingprovider',
    )
    meeting_status = sa.Enum(
        'Scheduled',
        'Live',
        'Completed',
        'Cancelled',
        name='meetingstatus',
    )
    project_status.create(op.get_bind(), checkfirst=True)
    project_priority.create(op.get_bind(), checkfirst=True)
    meeting_provider.create(op.get_bind(), checkfirst=True)
    meeting_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('industry', sa.String(length=255), nullable=True),
        sa.Column('client_name', sa.String(length=255), nullable=False),
        sa.Column('client_email', sa.String(length=255), nullable=True),
        sa.Column('client_company', sa.String(length=255), nullable=True),
        sa.Column('budget', sa.Numeric(12, 2), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='USD'),
        sa.Column('priority', project_priority, nullable=False, server_default='Medium'),
        sa.Column('status', project_status, nullable=False, server_default='Discovery'),
        sa.Column('expected_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expected_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_projects_company_id'), 'projects', ['company_id'])

    op.create_table(
        'meetings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider', meeting_provider, nullable=False, server_default='GOOGLE_MEET'),
        sa.Column('provider_meeting_id', sa.String(length=255), nullable=True),
        sa.Column('meeting_link', sa.String(length=500), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('agenda', sa.Text(), nullable=True),
        sa.Column('status', meeting_status, nullable=False, server_default='Scheduled'),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_meetings_project_id'), 'meetings', ['project_id'])

    op.create_table(
        'participants',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('company', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=100), nullable=True),
        sa.Column('attendance_status', sa.String(length=100), nullable=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('left_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_participants_meeting_id'), 'participants', ['meeting_id'])


def downgrade():
    op.drop_index(op.f('ix_participants_meeting_id'), table_name='participants')
    op.drop_table('participants')
    op.drop_index(op.f('ix_meetings_project_id'), table_name='meetings')
    op.drop_table('meetings')
    op.drop_index(op.f('ix_projects_company_id'), table_name='projects')
    op.drop_table('projects')

    meeting_status = sa.Enum(name='meetingstatus')
    meeting_provider = sa.Enum(name='meetingprovider')
    project_priority = sa.Enum(name='projectpriority')
    project_status = sa.Enum(name='projectstatus')

    meeting_status.drop(op.get_bind(), checkfirst=True)
    meeting_provider.drop(op.get_bind(), checkfirst=True)
    project_priority.drop(op.get_bind(), checkfirst=True)
    project_status.drop(op.get_bind(), checkfirst=True)
