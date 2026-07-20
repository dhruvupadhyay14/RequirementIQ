"""Provider-neutral, JSON-only LLM client with a safe offline fallback."""
import json
import os
from typing import Any

import requests


class LLMService:
    def __init__(self, provider: str | None = None) -> None:
        self.provider = (provider or os.getenv("AI_PROVIDER", "fallback")).lower()
        self.timeout = int(os.getenv("AI_REQUEST_TIMEOUT_SECONDS", "30"))

    def generate(self, prompt: str, context: str | None = None) -> dict[str, Any]:
        try:
            if self.provider == "openai" and os.getenv("OPENAI_API_KEY"):
                return self._openai(prompt, context or "")
            if self.provider == "gemini" and os.getenv("GEMINI_API_KEY"):
                return self._gemini(prompt, context or "")
        except (KeyError, IndexError, requests.RequestException, ValueError):
            # Analysis remains available when a provider is temporarily unavailable.
            return {}
        return {}

    def _openai(self, prompt: str, context: str) -> dict[str, Any]:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "Content-Type": "application/json"},
            json={
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "temperature": 0.1,
                "response_format": {"type": "json_object"},
                "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": context}],
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        return self._parse_json(response.json()["choices"][0]["message"]["content"])

    def _gemini(self, prompt: str, context: str) -> dict[str, Any]:
        model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={os.environ['GEMINI_API_KEY']}",
            json={"contents": [{"parts": [{"text": f"{prompt}\n\nMeeting transcript:\n{context}"}]}], "generationConfig": {"responseMimeType": "application/json", "temperature": 0.1}},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return self._parse_json(response.json()["candidates"][0]["content"]["parts"][0]["text"])

    @staticmethod
    def _parse_json(content: str) -> dict[str, Any]:
        content = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
