from uuid import UUID
from app.workspace_ai.memory_service import MemoryService

class WorkspaceContext:
    def __init__(self, db): self.memory = MemoryService(db)
    def build(self, workspace_id: UUID) -> str:
        values = self.memory.list(workspace_id)
        return "\n".join(f"- Preferred {item.category.replace('_', ' ')}: {item.value}" for item in values[:20])
