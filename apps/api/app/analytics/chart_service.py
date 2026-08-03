from collections import Counter
from datetime import datetime

class ChartService:
    @staticmethod
    def monthly(items, field="created_at"):
        counts = Counter(getattr(item, field).strftime("%Y-%m") for item in items if getattr(item, field, None))
        return [{"month": key, "value": value} for key, value in sorted(counts.items())]
    @staticmethod
    def status(projects): return [{"name": str(status.value if hasattr(status, "value") else status), "value": value} for status, value in Counter(item.status for item in projects).items()]
