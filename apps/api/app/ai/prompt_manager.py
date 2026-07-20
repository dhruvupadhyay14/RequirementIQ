from dataclasses import dataclass


@dataclass(frozen=True)
class PromptTemplate:
    name: str
    template: str


class PromptManager:
    def __init__(self) -> None:
        self.templates = {
            "requirement_extraction": PromptTemplate(
                name="requirement_extraction",
                template=(
                    "You are an expert business analyst and software architect. "
                    "Analyze the meeting transcript and extract software requirements. "
                    "Return valid JSON with the following structure: "
                    "{\"functional_requirements\": [], \"non_functional_requirements\": [], "
                    "\"business_requirements\": [], \"technical_requirements\": [], "
                    "\"missing_information\": [], \"questions\": []}. "
                    "Each requirement entry should include title, description, priority, confidence_score. "
                    "Each missing information item should include field, reason, severity. "
                    "Each question entry should include question, reason, status."
                ),
            ),
            "requirement_classification": PromptTemplate(
                name="requirement_classification",
                template=(
                    "Classify the requirement statement into one of: functional, non_functional, business, technical. "
                    "Return JSON with category and rationale."
                ),
            ),
            "question_generation": PromptTemplate(
                name="question_generation",
                template=(
                    "Based on the missing information fields, create concise follow-up questions for a software discovery session. "
                    "Return JSON with a list of questions and reasons."
                ),
            ),
            "json_response": PromptTemplate(
                name="json_response",
                template=(
                    "Return only valid JSON. Do not include markdown, commentary, or extra keys."
                ),
            ),
        }

    def get_template(self, key: str) -> PromptTemplate:
        if key not in self.templates:
            raise KeyError(f"Prompt template '{key}' not found")
        return self.templates[key]
