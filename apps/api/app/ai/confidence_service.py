from typing import Any


class ConfidenceService:
    def normalize(self, score: float | None) -> float:
        if score is None:
            return 0.0
        return max(0.0, min(1.0, float(score)))

    def build_confidence(self, base_score: float, factors: list[dict[str, Any]] | None = None) -> float:
        adjusted = self.normalize(base_score)
        if not factors:
            return adjusted

        for factor in factors:
            if factor.get("boost"):
                adjusted = min(1.0, adjusted + float(factor["boost"]))
        return adjusted
