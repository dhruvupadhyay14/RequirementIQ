from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas


class PDFService:
    def export(self, title: str, content: str) -> bytes:
        stream = BytesIO(); canvas = Canvas(stream, pagesize=A4); width, height = A4; y = height - 48
        for line in [title, "", *content.splitlines()]:
            words, current = line.split(), ""
            for word in words or [""]:
                candidate = f"{current} {word}".strip()
                if stringWidth(candidate, "Helvetica", 10) > width - 72:
                    canvas.drawString(36, y, current); y -= 14; current = word
                else: current = candidate
            canvas.drawString(36, y, current); y -= 14
            if y < 42: canvas.showPage(); y = height - 48
        canvas.save(); return stream.getvalue()
