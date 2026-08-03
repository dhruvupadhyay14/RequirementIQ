from app.analytics.chart_service import ChartService
from app.analytics.metrics_service import MetricsService
from app.analytics.report_service import ReportService
from types import SimpleNamespace
from datetime import datetime

def test_requirement_metrics():
    values = [SimpleNamespace(status="approved", category="functional", confidence_score=.8), SimpleNamespace(status="pending", category="technical", confidence_score=.6)]
    assert MetricsService.completion(values) == 50 and MetricsService.confidence_average(values) == .7

def test_chart_data_is_aggregated_by_month():
    values = [SimpleNamespace(created_at=datetime(2026, 1, 2)), SimpleNamespace(created_at=datetime(2026, 1, 4))]
    assert ChartService.monthly(values) == [{"month": "2026-01", "value": 2}]

def test_csv_export_contains_metrics():
    data, media, suffix = ReportService().export({"total_projects": 3}, "csv")
    assert media == "text/csv" and suffix == "csv" and b"total projects" in data


def test_excel_export_is_supported():
    data, media, suffix = ReportService().export({"total_projects": 3}, "excel")
    assert media == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" and suffix == "xlsx" and data.startswith(b"PK")
