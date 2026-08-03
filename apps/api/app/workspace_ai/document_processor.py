from io import BytesIO
from pathlib import Path
from docx import Document as WordDocument
from pypdf import PdfReader

class DocumentProcessor:
    ALLOWED = {".pdf", ".docx", ".txt", ".md", ".markdown"}
    def extract(self, file_name: str, content: bytes) -> str:
        extension = Path(file_name).suffix.lower()
        if extension not in self.ALLOWED: raise ValueError("Unsupported file type. Use PDF, DOCX, TXT, or Markdown.")
        if extension == ".pdf": return "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(content)).pages).strip()
        if extension == ".docx": return "\n".join(paragraph.text for paragraph in WordDocument(BytesIO(content)).paragraphs).strip()
        return content.decode("utf-8", errors="replace").strip()
