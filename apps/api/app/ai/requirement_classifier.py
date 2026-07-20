from typing import Any

from app.ai.llm_service import LLMService
from app.ai.prompt_manager import PromptManager


class RequirementClassifier:
    def __init__(self, llm_service: LLMService | None = None, prompt_manager: PromptManager | None = None) -> None:
        self.llm_service = llm_service or LLMService()
        self.prompt_manager = prompt_manager or PromptManager()

    def classify_requirement(self, statement: str) -> dict[str, Any]:
        text = statement.lower()
        if any(phrase in text for phrase in ["should be able", "can ", "create account", "check out", "manage "]):
            return {"category": "functional", "rationale": "The statement describes an expected user or system behavior."}
        if any(word in text for word in ["latency", "performance", "available", "availability", "responsive", "secure", "security", "compliance", "scalable", "within", "response time"]):
            return {"category": "non_functional", "rationale": "The statement defines a quality attribute or constraint."}
        if any(word in text for word in ["integrate", "api", "database", "hosting", "deploy", "technology", "stripe"]):
            return {"category": "technical", "rationale": "The statement specifies an implementation or integration concern."}
        if any(word in text for word in ["revenue", "sales", "growth", "reduce cost", "business goal"]):
            return {"category": "business", "rationale": "The statement defines a business outcome."}
        prompt = self.prompt_manager.get_template("requirement_classification").template
        result = self.llm_service.generate(prompt, statement)
        if isinstance(result, dict) and result.get("category") in {"functional", "non_functional", "business", "technical"}:
            return result
        return {"category": "functional", "rationale": "Default classification for unstructured text."}
