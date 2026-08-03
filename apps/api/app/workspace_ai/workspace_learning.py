from uuid import UUID
from sqlalchemy.orm import Session
from app.models.requirement import Requirement
from app.workspace_ai.memory_service import MemoryService

class WorkspaceLearning:
    def __init__(self, db: Session): self.db, self.memory = db, MemoryService(db)
    def learn_from_meeting(self, workspace_id: UUID, meeting_id: UUID) -> int:
        requirements = self.db.query(Requirement).filter(Requirement.meeting_id == meeting_id, Requirement.status == "approved").all(); learned = 0
        for item in requirements:
            text = f"{item.title} {item.description or ''}".lower()
            for keyword, category in [("aws", "deployment_preference"), ("azure", "deployment_preference"), ("react", "technology_preference"), ("python", "technology_preference"), ("security", "security_preference"), ("mobile", "ui_preference"), ("api", "architecture_preference")]:
                if keyword in text: self.memory.remember(workspace_id, category, keyword, "approved_requirement"); learned += 1
        self.db.commit(); return learned
