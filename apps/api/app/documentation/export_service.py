from app.documentation.docx_service import DOCXService
from app.documentation.pdf_service import PDFService


class ExportService:
    def __init__(self): self.pdf, self.docx = PDFService(), DOCXService()
    def export(self, format_name: str, title: str, content: str) -> tuple[bytes, str, str]:
        if format_name == "markdown": return content.encode(), "text/markdown", "md"
        if format_name == "pdf": return self.pdf.export(title, content), "application/pdf", "pdf"
        if format_name == "docx": return self.docx.export(title, content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "docx"
        raise ValueError("Unsupported export format")
