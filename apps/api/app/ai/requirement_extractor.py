from typing import Any

from app.ai.confidence_service import ConfidenceService
from app.ai.llm_service import LLMService
from app.ai.prompt_manager import PromptManager
from app.ai.question_generator import QuestionGenerator
from app.ai.requirement_classifier import RequirementClassifier


class RequirementExtractor:
    def __init__(
        self,
        llm_service: LLMService | None = None,
        prompt_manager: PromptManager | None = None,
        confidence_service: ConfidenceService | None = None,
        classifier: RequirementClassifier | None = None,
        question_generator: QuestionGenerator | None = None,
    ) -> None:
        self.llm_service = llm_service or LLMService()
        self.prompt_manager = prompt_manager or PromptManager()
        self.confidence_service = confidence_service or ConfidenceService()
        self.classifier = classifier or RequirementClassifier(self.llm_service, self.prompt_manager)
        self.question_generator = question_generator or QuestionGenerator(self.llm_service, self.prompt_manager)

    def extract_requirements(self, transcript: str) -> dict[str, Any]:
        prompt = self.prompt_manager.get_template("requirement_extraction").template
        result = self.llm_service.generate(prompt, transcript)

        if not isinstance(result, dict) or not result:
            result = self._heuristic_result(transcript)
        normalized = self._normalize_result(result)
        if not normalized["missing_information"]:
            normalized["missing_information"] = self._detect_missing_information(transcript)
        if not normalized["questions"]:
            normalized["questions"] = self.question_generator.generate_questions([entry["field"] for entry in normalized["missing_information"]], transcript)
        return normalized

    def _heuristic_result(self, transcript: str) -> dict[str, Any]:
        text = transcript.lower()
        functional, non_functional, business, technical = [], [], [], []
        if any(term in text for term in ["website", "app", "platform", "system"]):
            functional.append({"title": "Core application experience", "description": "Provide the requested digital product and its primary user journeys.", "priority": "high", "confidence_score": 0.7})
        if any(term in text for term in ["account", "login", "sign up", "customer"]):
            functional.append({"title": "User account management", "description": "Users should be able to create and access their accounts.", "priority": "high", "confidence_score": 0.84})
        if any(term in text for term in ["cart", "checkout", "order", "inventory", "admin"]):
            functional.append({"title": "Commerce and administration workflow", "description": "Support the business workflow described in the meeting.", "priority": "high", "confidence_score": 0.82})
        if any(term in text for term in ["mobile", "responsive", "fast", "performance"]):
            non_functional.append({"title": "Responsive performance", "description": "The solution should provide a fast, usable experience across requested devices.", "priority": "high", "confidence_score": 0.78})
        if any(term in text for term in ["sell", "sales", "revenue", "ecommerce", "e-commerce"]):
            business.append({"title": "Digital commerce enablement", "description": "Enable the stated commercial goal through the digital solution.", "priority": "high", "confidence_score": 0.8})
        if any(term in text for term in ["stripe", "payment", "api", "integration"]):
            technical.append({"title": "Third-party service integration", "description": "Integrate the external service required by the proposed workflow.", "priority": "high", "confidence_score": 0.8})
        return {"functional_requirements": functional, "non_functional_requirements": non_functional, "business_requirements": business, "technical_requirements": technical, "missing_information": [], "questions": []}

    @staticmethod
    def _detect_missing_information(transcript: str) -> list[dict[str, str]]:
        text = transcript.lower()
        checks = {
            "target_users": (["target user", "customer", "audience", "user"], "The primary users were not clearly identified."),
            "user_roles": (["role", "admin", "manager", "customer"], "Required user roles and permissions were not defined."),
            "budget": (["budget", "cost", "price"], "No delivery budget or range was discussed."),
            "timeline": (["timeline", "deadline", "launch", "milestone"], "No delivery timeline or milestone was discussed."),
            "integrations": (["integration", "stripe", "api", "payment gateway"], "Required third-party integrations were not fully identified."),
            "authentication": (["login", "sign in", "authentication", "sso"], "The authentication approach was not defined."),
            "security_requirements": (["security", "compliance", "gdpr", "encryption"], "Security and compliance expectations were not defined."),
            "deployment_preferences": (["cloud", "aws", "azure", "on-premise", "deployment"], "The deployment environment was not defined."),
            "platforms": (["web", "ios", "android", "mobile", "platform"], "The target platforms were not fully defined."),
        }
        return [{"field": field, "reason": reason, "severity": "high" if field in {"security_requirements", "authentication"} else "medium"} for field, (terms, reason) in checks.items() if not any(term in text for term in terms)]

    def _normalize_result(self, result: dict[str, Any]) -> dict[str, Any]:
        normalized = {
            "functional_requirements": [],
            "non_functional_requirements": [],
            "business_requirements": [],
            "technical_requirements": [],
            "missing_information": [],
            "questions": [],
        }

        for key in ["functional_requirements", "non_functional_requirements", "business_requirements", "technical_requirements"]:
            items = result.get(key, []) or []
            normalized[key] = []
            for item in items:
                if isinstance(item, dict):
                    normalized[key].append(
                        {
                            "title": item.get("title") or "Untitled requirement",
                            "description": item.get("description") or "",
                            "priority": item.get("priority") or "medium",
                            "confidence_score": self.confidence_service.normalize(item.get("confidence_score")),
                            "category": item.get("category") or key.replace("_requirements", ""),
                        }
                    )

        missing_information = result.get("missing_information", []) or []
        normalized["missing_information"] = [
            {
                "field": item.get("field") or item.get("name") or "unknown",
                "reason": item.get("reason") or "",
                "severity": item.get("severity") or "medium",
            }
            for item in missing_information
            if isinstance(item, dict)
        ]

        questions = result.get("questions", []) or []
        normalized["questions"] = [
            {
                "question": item.get("question") or "",
                "reason": item.get("reason") or "",
                "status": item.get("status") or "pending",
            }
            for item in questions
            if isinstance(item, dict)
        ]

        return normalized
