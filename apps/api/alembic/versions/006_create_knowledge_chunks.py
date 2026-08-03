from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "006_create_knowledge_chunks"
down_revision = "005_create_documents_table"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("knowledge_chunks", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("meeting_id", postgresql.UUID(as_uuid=True), nullable=True), sa.Column("source_type", sa.String(50), nullable=False), sa.Column("chunk_text", sa.Text(), nullable=False), sa.Column("embedding_id", sa.String(255), nullable=False, unique=True), sa.Column("metadata", postgresql.JSONB(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")), sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"], ondelete="CASCADE"))
    op.create_index("ix_knowledge_chunks_project_id", "knowledge_chunks", ["project_id"])
    op.create_index("ix_knowledge_chunks_meeting_id", "knowledge_chunks", ["meeting_id"])

def downgrade() -> None:
    op.drop_index("ix_knowledge_chunks_meeting_id", table_name="knowledge_chunks"); op.drop_index("ix_knowledge_chunks_project_id", table_name="knowledge_chunks"); op.drop_table("knowledge_chunks")
