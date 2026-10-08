import io
from fpdf import FPDF

def text_to_pdf(text, font_path="DejaVuSans.ttf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", font_path)
    pdf.set_font("DejaVu", size=12)
    pdf.multi_cell(0, 7, text)  # сам переносит строки и добавляет новые страницы
    return io.BytesIO(bytes(pdf.output()))