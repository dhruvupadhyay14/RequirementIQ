class ContextBuilder:
    def build(self, results: list[dict], max_characters: int = 5000) -> str:
        sections, used = [], 0
        for result in results:
            text = result["text"].strip(); source = result["metadata"].get("source_type", "knowledge")
            part = f"[{source}] {text}"
            if used + len(part) > max_characters: break
            sections.append(part); used += len(part)
        return "\n\n".join(sections)
