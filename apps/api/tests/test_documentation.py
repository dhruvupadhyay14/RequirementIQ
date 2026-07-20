from types import SimpleNamespace
from app.documentation.docx_service import DOCXService
from app.documentation.pdf_service import PDFService
from app.documentation.template_manager import TemplateManager


def context():
    return {"project": SimpleNamespace(title="Commerce", description="Sell online", expected_end_date=None), "meeting": SimpleNamespace(title="Discovery", scheduled_at="2026-01-01", agenda="Scope", description=None), "requirements": [SimpleNamespace(category="functional", title="Checkout", description="Customers can pay")], "questions": [], "participants": [SimpleNamespace(name="Sam", role="Client")], "transcript": "We discussed checkout."}


def test_srs_template_contains_required_sections():
    output = TemplateManager().render("srs", context())
    assert "1. Introduction" in output and "4. Functional Requirements" in output and "Checkout" in output


def test_pdf_export_creates_pdf_bytes():
    assert PDFService().export("Test", "# Heading\nContent").startswith(b"%PDF")


def test_docx_export_creates_docx_bytes():
    assert DOCXService().export("Test", "## Heading\nContent").startswith(b"PK")
