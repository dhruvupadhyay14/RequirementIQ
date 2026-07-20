from typing import Any

from app.ai.llm_service import LLMService
from app.ai.prompt_manager import PromptManager


class QuestionGenerator:
    def __init__(self, llm_service: LLMService | None = None, prompt_manager: PromptManager | None = None) -> None:
        self.llm_service = llm_service or LLMService()
        self.prompt_manager = prompt_manager or PromptManager()

    def generate_questions(self, missing_fields: list[str], context: str | None = None) -> list[dict[str, Any]]:
        fallback = []
        for field in missing_fields:
            if field == "target_users":
                fallback.append({"question": "Who are the primary target users for this solution?", "reason": "Target audience affects the product experience.", "status": "pending"})
            elif field == "user_roles":
                fallback.append({"question": "Will there be multiple user roles such as admin, customer, or manager?", "reason": "Roles define permissions and workflow complexity.", "status": "pending"})
            elif field == "integrations":
                fallback.append({"question": "Which payment gateway and other third-party services should the solution integrate with?", "reason": "Integrations shape architecture and delivery scope.", "status": "pending"})
            elif field == "timeline":
                fallback.append({"question": "What is the desired launch timeline or milestone?", "reason": "Timeline influences prioritization and delivery planning.", "status": "pending"})
            elif field == "budget":
                fallback.append({"question": "What budget range are you planning for this initiative?", "reason": "Budget constraints influence implementation choices.", "status": "pending"})
            elif field == "technology_preferences":
                fallback.append({"question": "Do you have preferred technologies or platforms for the build?", "reason": "Technology preferences affect stack decisions.", "status": "pending"})
            elif field == "security_requirements":
                fallback.append({"question": "Do you have specific security or compliance requirements?", "reason": "Security needs influence architecture and controls.", "status": "pending"})
            elif field == "deployment_preferences":
                fallback.append({"question": "Would you prefer cloud, on-premises, or hybrid deployment?", "reason": "Deployment preferences shape infrastructure choices.", "status": "pending"})
            elif field == "authentication":
                fallback.append({"question": "How should users authenticate: email/password, SSO, or social login?", "reason": "Authentication determines identity and access architecture.", "status": "pending"})
            elif field == "platforms":
                fallback.append({"question": "Which platforms must be supported: web, iOS, Android, or all three?", "reason": "Platform scope materially affects delivery effort.", "status": "pending"})
        if not fallback:
            fallback.append({"question": "What additional context would you like the team to clarify?", "reason": "Missing details can change scope and delivery decisions.", "status": "pending"})
        return fallback
