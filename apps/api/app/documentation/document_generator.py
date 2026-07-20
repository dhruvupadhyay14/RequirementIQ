from app.documentation.template_manager import TemplateManager


class DocumentGenerator:
    def __init__(self, templates: TemplateManager | None = None):
        self.templates = templates or TemplateManager()

    def generate(self, document_type: str, context: dict) -> tuple[str, str]:
        if document_type not in self.templates.TITLES:
            raise ValueError("Unsupported document type")
        return self.templates.TITLES[document_type], self.templates.render(document_type, context)
