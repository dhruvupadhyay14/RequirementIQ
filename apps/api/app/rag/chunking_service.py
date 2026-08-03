class ChunkingService:
    def __init__(self, chunk_size: int = 900, overlap: int = 150): self.chunk_size, self.overlap = chunk_size, overlap
    def chunk(self, text: str) -> list[str]:
        text = " ".join(text.split())
        if not text: return []
        chunks, start = [], 0
        while start < len(text):
            end = min(len(text), start + self.chunk_size)
            if end < len(text): end = text.rfind(" ", start, end) or end
            chunks.append(text[start:end].strip())
            if end == len(text): break
            start = max(end - self.overlap, start + 1)
        return chunks
