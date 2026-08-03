from app.workspace_ai.document_processor import DocumentProcessor
from app.workspace_ai.memory_service import MemoryService

def test_document_processor_supports_txt_and_markdown():
    assert DocumentProcessor().extract("architecture.md", b"# Architecture\nUse React and FastAPI") == "# Architecture\nUse React and FastAPI"

def test_document_processor_rejects_unknown_extensions():
    try: DocumentProcessor().extract("archive.zip", b"x")
    except ValueError as error: assert "Unsupported" in str(error)
    else: assert False

def test_memory_service_records_preference():
    class Query:
        def filter(self, *args): return self
        def first(self): return None
    class DB:
        def __init__(self): self.items = []
        def query(self, *args): return Query()
        def add(self, item): self.items.append(item)
    item = MemoryService(DB()).remember("workspace", "technology_preference", "react", "test")
    assert item.value == "react" and item.category == "technology_preference"
