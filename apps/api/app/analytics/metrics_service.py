from collections import Counter

class MetricsService:
    @staticmethod
    def completion(requirements):
        if not requirements: return 0
        return round(100 * sum(item.status == "approved" for item in requirements) / len(requirements))
    @staticmethod
    def confidence_average(requirements):
        return round(sum(float(item.confidence_score) for item in requirements) / len(requirements), 2) if requirements else 0
    @staticmethod
    def categories(requirements): return [{"name": name.replace("_", " ").title(), "value": value} for name, value in Counter(item.category for item in requirements).items()]
