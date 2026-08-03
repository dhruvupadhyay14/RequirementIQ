import csv
from io import BytesIO, StringIO
from app.documentation.pdf_service import PDFService

class ReportService:
    def export(self, overview: dict, format_name: str):
        rows = [{"metric": key.replace("_", " "), "value": value} for key, value in overview.items() if isinstance(value, (int, float, str))]
        if format_name == "csv":
            stream = StringIO(); writer = csv.DictWriter(stream, fieldnames=["metric", "value"]); writer.writeheader(); writer.writerows(rows); return stream.getvalue().encode(), "text/csv", "csv"
        if format_name == "pdf": return PDFService().export("RequirementIQ Analytics", "\n".join(f"{item['metric']}: {item['value']}" for item in rows)), "application/pdf", "pdf"
        if format_name == "excel":
            from openpyxl import Workbook
            workbook = Workbook(); sheet = workbook.active; sheet.append(["Metric", "Value"])
            for item in rows: sheet.append([item["metric"], item["value"]])
            stream = BytesIO(); workbook.save(stream); return stream.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "xlsx"
        raise ValueError("Unsupported export format")
